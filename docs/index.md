<p align="center">
  <img src="assets/social-preview.png" alt="Pydantic AI Shields" width="100%">
</p>

<h1 align="center">Pydantic AI Shields</h1>

<p align="center"><em>Drop-in guardrails for your AI agents.</em></p>

<p align="center">
  <a href="https://pypi.org/project/pydantic-ai-shields/"><img src="https://img.shields.io/pypi/v/pydantic-ai-shields.svg" alt="PyPI version"></a>
  <a href="https://pepy.tech/projects/pydantic-ai-shields"><img src="https://static.pepy.tech/badge/pydantic-ai-shields/month" alt="PyPI Downloads"></a>
  <a href="https://github.com/vstorm-co/pydantic-ai-shields/stargazers"><img src="https://img.shields.io/github/stars/vstorm-co/pydantic-ai-shields?style=flat&logo=github&color=yellow" alt="GitHub Stars"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/vstorm-co/pydantic-ai-shields/actions/workflows/ci.yml"><img src="https://github.com/vstorm-co/pydantic-ai-shields/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/pydantic/pydantic-ai"><img src="https://img.shields.io/badge/Powered%20by-Pydantic%20AI-E92063?logo=pydantic&logoColor=white" alt="Pydantic AI"></a>
</p>

---

!!! info "Upstreamed to `pydantic-ai-harness`"
    Working together with the Pydantic team, we are moving this library's functionality into the official
    [pydantic-ai-harness](https://github.com/pydantic/pydantic-ai-harness), where it lives as
    [`pydantic_ai_harness/guardrails`](https://github.com/pydantic/pydantic-ai-harness/tree/main/pydantic_ai_harness/guardrails).

    **For new projects, use the harness.** `InputGuard` / `OutputGuard` / `ToolGuard` are upstream today as
    `InputGuardrail` / `OutputGuardrail` / `ToolGuardrail`
    ([#249](https://github.com/pydantic/pydantic-ai-harness/pull/249),
    [#470](https://github.com/pydantic/pydantic-ai-harness/pull/470)); the content shields
    ([#478](https://github.com/pydantic/pydantic-ai-harness/pull/478)) and cost budgets
    ([#474](https://github.com/pydantic/pydantic-ai-harness/pull/474)) are in review. This library stays on
    PyPI and keeps working for everyone already depending on it. The
    [README](https://github.com/vstorm-co/pydantic-ai-shields#readme) has the full mapping.

    ```python
    from pydantic_ai import Agent
    from pydantic_ai_harness.guardrails import InputGuardrail, ToolGuardrail

    agent = Agent(
        "openai:gpt-5.4",
        capabilities=[
            InputGuardrail(guard=no_secrets),
            ToolGuardrail(guard=stay_in_the_workspace, result_guard=scrub_secrets),
        ],
    )
    ```

!!! tip "Part of Pydantic Deep Agents"
    **Pydantic AI Shields** is one library in [Pydantic Deep Agents](https://github.com/vstorm-co/pydantic-deepagents) — the open-source
    Claude Code alternative & Python agent framework. Use it standalone, or get every
    library wired together in a single `create_deep_agent()` call.

**Pydantic AI Shields** provides ready-to-use guardrail [capabilities](https://ai.pydantic.dev/capabilities/) for [Pydantic AI](https://ai.pydantic.dev/) agents. Drop them into any agent for cost control, tool permissions, content safety, and more.

## Quick Start

```python
from pydantic_ai import Agent
from pydantic_ai_shields import (
    CostTracking, PromptInjection, PiiDetector, SecretRedaction,
)

agent = Agent(
    "openai:gpt-4.1",
    capabilities=[
        CostTracking(budget_usd=5.0),
        PromptInjection(sensitivity="high"),
        PiiDetector(),
        SecretRedaction(),
    ],
)
```

## Available Shields

### Infrastructure Shields

| Shield | Description |
|--------|-------------|
| [`CostTracking`][pydantic_ai_shields.guardrails.CostTracking] | Token/USD tracking with budget enforcement |
| [`ToolGuard`][pydantic_ai_shields.guardrails.ToolGuard] | Block tools or require human approval |
| [`InputGuard`][pydantic_ai_shields.guardrails.InputGuard] | Custom input validation (pluggable function) |
| [`OutputGuard`][pydantic_ai_shields.guardrails.OutputGuard] | Custom output validation (pluggable function) |
| [`AsyncGuardrail`][pydantic_ai_shields.guardrails.AsyncGuardrail] | Run guard concurrently with LLM call |

### Content Shields

| Shield | Description |
|--------|-------------|
| [`PromptInjection`][pydantic_ai_shields.shields.PromptInjection] | Detect prompt injection / jailbreak (6 categories, 3 sensitivity levels) |
| [`PiiDetector`][pydantic_ai_shields.shields.PiiDetector] | Detect PII — email, phone, SSN, credit card, IP |
| [`SecretRedaction`][pydantic_ai_shields.shields.SecretRedaction] | Block API keys, tokens, credentials in output |
| [`BlockedKeywords`][pydantic_ai_shields.shields.BlockedKeywords] | Block forbidden keywords/phrases |
| [`NoRefusals`][pydantic_ai_shields.shields.NoRefusals] | Block LLM refusals ("I cannot help with that") |

## Next Steps

- [Installation](installation.md) — install the package
- [Examples](examples/index.md) — real-world usage patterns
- [API Reference](api/index.md) — full API docs
