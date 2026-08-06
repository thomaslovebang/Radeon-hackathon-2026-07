# Lobster 工作流 (预留)

> 对应 spec `autoflow_spec_lobster_integration.md` (v2.1)。
> MVP 阶段 CLI 直接调用 OpenAdapt，此目录预留 Lobster 编排集成。

## 说明

Lobster 是 OpenClaw 原生的 YAML 工作流引擎，提供：
- 步骤编排 (steps / run)
- 审批门控 (approval: required)
- 条件分支 (when / condition)
- 数据传递 ($stepId.stdout / $stepId.json)
- 恢复机制 (resumeToken)

## 计划工作流

| 文件 | 用途 |
|------|------|
| `learn-skill.lobster` | 演示录制 -> 编译 -> 注册 |
| `run-skill.lobster` | 语义匹配 -> 参数注入 -> replay |
| `repair-skill.lobster` | Halt -> 诊断 -> 审批 -> 版本化 |

## 集成方式

MVP 阶段 CLI 命令已实现等价逻辑 (create/run/repair)，后续可通过 Lobster
将这些 CLI 命令串成带审批门控的完整工作流。
