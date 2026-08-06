"""Headless browser execution for silent web tasks."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class HeadlessBrowser:
    """A single-task Playwright browser controlled through stable element IDs."""

    MAX_ELEMENTS = 150
    MAX_TEXT = 30_000
    _SAFE_ID = re.compile(r"^b\d{3}$")

    def __init__(self, downloads_dir: Path | None = None) -> None:
        self.downloads_dir = downloads_dir or (Path.home() / "Downloads" / "AutoFlow")
        self._playwright: Any = None
        self._browser: Any = None
        self._context: Any = None
        self._page: Any = None
        self._elements: dict[str, dict[str, str]] = {}

    @property
    def active(self) -> bool:
        return self._page is not None

    def open(self, target: str) -> dict[str, Any]:
        url = self._normalize_url(target)
        page = self._ensure_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        except Exception as exc:
            if not page.url or page.url == "about:blank":
                raise RuntimeError(f"后台浏览器无法打开 {url}：{exc}") from exc
        result = self.observe()
        result["message"] = f"已在后台浏览器打开：{result['title'] or result['url']}"
        return result

    def observe(self) -> dict[str, Any]:
        page = self._require_page()
        self._elements = {}
        elements: list[dict[str, Any]] = []
        candidates = page.locator(
            "a[href],button,input:not([type=hidden]),textarea,select,"
            "[role=button],[role=link],[contenteditable=true]"
        )
        for index in range(min(candidates.count(), self.MAX_ELEMENTS)):
            locator = candidates.nth(index)
            try:
                if not locator.is_visible():
                    continue
                element_id = f"b{len(elements) + 1:03d}"
                details = locator.evaluate(
                    """element => ({
                        tag: element.tagName.toLowerCase(),
                        type: element.getAttribute('type') || '',
                        role: element.getAttribute('role') || '',
                        name: element.getAttribute('aria-label') ||
                              element.innerText || element.getAttribute('placeholder') ||
                              element.getAttribute('title') || element.getAttribute('name') || '',
                        href: element.href || '',
                        disabled: Boolean(element.disabled || element.getAttribute('aria-disabled') === 'true')
                    })"""
                )
                locator.evaluate("(element, id) => element.setAttribute('data-autoflow-id', id)", element_id)
                name = " ".join(str(details.get("name", "")).split())[:240]
                element = {
                    "id": element_id,
                    "name": name,
                    "type": details.get("role") or details.get("type") or details.get("tag") or "element",
                    "href": str(details.get("href", ""))[:500],
                    "enabled": not bool(details.get("disabled", False)),
                }
                elements.append(element)
                self._elements[element_id] = {"name": name, "type": str(element["type"])}
            except Exception:
                continue
        text = page.locator("body").inner_text(timeout=5_000)[: self.MAX_TEXT]
        return {
            "ok": True,
            "headless": True,
            "url": page.url,
            "title": page.title(),
            "text": text,
            "elements": elements,
            "truncated": len(text) == self.MAX_TEXT or candidates.count() > self.MAX_ELEMENTS,
        }

    def click(self, element_id: str) -> dict[str, Any]:
        locator = self._locator(element_id)
        locator.click(timeout=10_000)
        self._page.wait_for_timeout(250)
        result = self.observe()
        result["message"] = f"已在后台浏览器点击 {element_id}"
        return result

    def type_text(self, element_id: str, text: str, replace: bool = True) -> dict[str, Any]:
        locator = self._locator(element_id)
        if replace:
            locator.fill(text, timeout=10_000)
        else:
            locator.type(text, timeout=10_000)
        return {"ok": True, "headless": True, "url": self._page.url, "message": f"已在后台浏览器向 {element_id} 输入 {len(text)} 个字符"}

    def select(self, element_id: str, option: str) -> dict[str, Any]:
        locator = self._locator(element_id)
        try:
            selected = locator.select_option(label=option, timeout=10_000)
        except Exception:
            selected = locator.select_option(value=option, timeout=10_000)
        return {"ok": True, "headless": True, "url": self._page.url, "selected": selected, "message": f"已在后台浏览器选择：{option}"}

    def press(self, keys: str) -> dict[str, Any]:
        page = self._require_page()
        normalized = "+".join(part.strip().title() for part in keys.split("+") if part.strip())
        if not normalized or len(normalized) > 80:
            raise ValueError("浏览器按键格式不正确。")
        page.keyboard.press(normalized)
        return {"ok": True, "headless": True, "url": page.url, "message": f"已在后台浏览器发送按键：{normalized}"}

    def back(self) -> dict[str, Any]:
        page = self._require_page()
        page.go_back(wait_until="domcontentloaded", timeout=15_000)
        result = self.observe()
        result["message"] = "后台浏览器已返回上一页"
        return result

    def download(self, element_id: str) -> dict[str, Any]:
        page = self._require_page()
        locator = self._locator(element_id)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        try:
            with page.expect_download(timeout=15_000) as download_info:
                locator.click(timeout=10_000)
            download = download_info.value
        except Exception as exc:
            raise RuntimeError("该控件没有触发可保存的下载，可能需要登录或网站阻止了下载。") from exc
        filename = Path(download.suggested_filename).name or "download"
        destination = self._unique_destination(filename)
        download.save_as(str(destination))
        return {
            "ok": True,
            "headless": True,
            "url": page.url,
            "path": str(destination.resolve()),
            "message": f"文件已下载到：{destination.resolve()}",
        }

    def element_summary(self, element_id: str) -> dict[str, str] | None:
        return self._elements.get(element_id)

    def close(self) -> None:
        self._elements = {}
        for item_name in ("_context", "_browser"):
            item = getattr(self, item_name)
            if item is not None:
                try:
                    item.close()
                except Exception:
                    pass
                setattr(self, item_name, None)
        if self._playwright is not None:
            try:
                self._playwright.stop()
            except Exception:
                pass
        self._playwright = None
        self._page = None

    def _ensure_page(self) -> Any:
        if self._page is not None:
            return self._page
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError("缺少后台浏览器组件，请重新运行 pip install -e .") from exc
        self._playwright = sync_playwright().start()
        executable = self._browser_executable()
        launch_options: dict[str, Any] = {"headless": True, "args": ["--disable-notifications", "--disable-popup-blocking"]}
        if executable:
            launch_options["executable_path"] = str(executable)
        try:
            self._browser = self._playwright.chromium.launch(**launch_options)
            self._context = self._browser.new_context(locale="zh-CN", accept_downloads=True)
            self._page = self._context.new_page()
            return self._page
        except Exception as exc:
            self.close()
            raise RuntimeError(f"无法启动后台浏览器：{exc}") from exc

    def _locator(self, element_id: str) -> Any:
        page = self._require_page()
        if not self._SAFE_ID.fullmatch(element_id) or element_id not in self._elements:
            raise ValueError(f"网页控件 {element_id} 已失效，请重新调用 browser_observe。")
        locator = page.locator(f'[data-autoflow-id="{element_id}"]').first
        if locator.count() != 1:
            raise ValueError(f"网页控件 {element_id} 已失效，请重新调用 browser_observe。")
        return locator

    def _require_page(self) -> Any:
        if self._page is None:
            raise ValueError("后台浏览器尚未打开网页，请先调用 browser_open。")
        return self._page

    def _unique_destination(self, filename: str) -> Path:
        candidate = self.downloads_dir / filename
        stem, suffix = candidate.stem, candidate.suffix
        index = 1
        while candidate.exists():
            candidate = self.downloads_dir / f"{stem}-{index}{suffix}"
            index += 1
        return candidate

    @staticmethod
    def _normalize_url(target: str) -> str:
        value = target.strip()
        if not value:
            raise ValueError("缺少网页地址。")
        if "://" not in value and re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
            raise ValueError("后台浏览器只允许打开 http 或 https 网页。")
        if "://" not in value:
            value = "https://" + value
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("后台浏览器只允许打开 http 或 https 网页。")
        return value

    @staticmethod
    def _browser_executable() -> Path | None:
        configured = os.environ.get("AUTOFLOW_BROWSER_EXECUTABLE", "").strip()
        candidates = [
            Path(configured) if configured else None,
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        ]
        return next((path for path in candidates if path is not None and path.is_file()), None)
