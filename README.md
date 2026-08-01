<p align="center">
  <img src="assets/social-preview.png" alt="Pydantic AI Shields" width="100%">
</p>

<h1 align="center">Pydantic AI Shields</h1>

<p align="center">
  <b>Drop-in guardrails for your AI agents.</b><br>
  Cost & budget caps, input / output / tool blocking, PII & secret redaction — for any Pydantic AI agent.
</p>

<p align="center">
  <a href="https://vstorm-co.github.io/pydantic-ai-shields/">Docs</a> &middot;
  <a href="https://pypi.org/project/pydantic-ai-shields/">PyPI</a> &middot;
  <a href="#installation">Install</a> &middot;
  <a href="#vstorm-oss-ecosystem">Ecosystem</a> &middot;
  <a href="https://github.com/vstorm-co/pydantic-deepagents">Deep Agents</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/pydantic-ai-shields/"><img src="https://img.shields.io/pypi/v/pydantic-ai-shields.svg" alt="PyPI version"></a>
  <a href="https://pepy.tech/projects/pydantic-ai-shields"><img src="https://static.pepy.tech/badge/pydantic-ai-shields/month" alt="PyPI Downloads"></a>
  <a href="https://github.com/vstorm-co/pydantic-ai-shields/stargazers"><img src="https://img.shields.io/github/stars/vstorm-co/pydantic-ai-shields?style=flat&logo=github&color=yellow" alt="GitHub Stars"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/vstorm-co/pydantic-ai-shields/actions/workflows/ci.yml"><img src="https://github.com/vstorm-co/pydantic-ai-shields/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/pydantic/pydantic-ai"><img src="https://img.shields.io/badge/Powered%20by-Pydantic%20AI-E92063?logo=pydantic&logoColor=white" alt="Pydantic AI"></a>
</p>

<p align="center">
  <b>Cost &amp; budget caps</b> &nbsp;&bull;&nbsp; <b>Prompt-injection defense</b> &nbsp;&bull;&nbsp; <b>PII detection</b> &nbsp;&bull;&nbsp; <b>Secret redaction</b> &nbsp;&bull;&nbsp; <b>Tool permissions</b> &nbsp;&bull;&nbsp; <b>Async guardrails</b>
</p>

---

> ### ⬆️ Upstreamed to `pydantic-ai-harness`
>
> Working together with the Pydantic team, we are moving this library's functionality into the official
> **[pydantic-ai-harness](https://github.com/pydantic/pydantic-ai-harness)**, where it lives as
> [`pydantic_ai_harness/guardrails`](https://github.com/pydantic/pydantic-ai-harness/tree/main/pydantic_ai_harness/guardrails).
>
> **For new projects, use the harness** — it is maintained by Pydantic alongside Pydantic AI itself. This
> repository stays on PyPI and keeps working for everyone already depending on it.
>
> ```python
> from pydantic_ai import Agent
> from pydantic_ai_harness.guardrails import InputGuardrail, ToolGuardrail
>
> agent = Agent(
>     "openai:gpt-5.4",
>     capabilities=[
>         InputGuardrail(guard=no_secrets),
>         ToolGuardrail(guard=stay_in_the_workspace, result_guard=scrub_secrets),
>     ],
> )
> ```
>
> **Landed upstream**
>
> | This library | In `pydantic_ai_harness.guardrails` | PR |
> |---|---|---|
> | `InputGuard` | `InputGuardrail` | [#219](https://github.com/pydantic/pydantic-ai-harness/pull/219), merged as [#249](https://github.com/pydantic/pydantic-ai-harness/pull/249) |
> | `OutputGuard` | `OutputGuardrail` | [#219](https://github.com/pydantic/pydantic-ai-harness/pull/219), merged as [#249](https://github.com/pydantic/pydantic-ai-harness/pull/249) |
> | `ToolGuard` (`blocked`, `require_approval`) | `ToolGuardrail` — a `guard` over the tool's arguments plus a `result_guard` over what it returned; approval is the `approve` outcome | [#470](https://github.com/pydantic/pydantic-ai-harness/pull/470) |
> | `AsyncGuardrail(timing="concurrent")` | `InputGuardrail(parallel=True)` | [#249](https://github.com/pydantic/pydantic-ai-harness/pull/249) |
>
> Upstream a guard returns a `GuardrailResult` rather than a bare `bool`, so besides **allow** and **block** it
> can **replace** the value (redaction), **retry** an output, or ask for **approval** on a tool call.
>
> **In review**
>
> | This library | Upstream | PR |
> |---|---|---|
> | `PromptInjection`, `PiiDetector`, `SecretRedaction`, `BlockedKeywords` | `guardrails.detectors` — `redact_secrets`, `redact_personal_data`, `blocked_keywords([...])` — plus guard chains (`guard=[...]`), so a redactor placed first cleans the text every later check reads | [#478](https://github.com/pydantic/pydantic-ai-harness/pull/478) |
> | `CostTracking(budget_usd=...)` | `SpendLimits` — spend and token budgets over windows longer than a single run, shareable across worker processes | [#474](https://github.com/pydantic/pydantic-ai-harness/pull/474) |
>
> `NoRefusals` has no upstream equivalent.

> **Part of [Pydantic Deep Agents](https://github.com/vstorm-co/pydantic-deepagents)** — the open-source Claude Code alternative & Python agent framework. Use this library standalone, or get everything wired together in one `create_deep_agent()` call.

**Pydantic AI Shields** are ready-to-use guardrail [capabilities](https://ai.pydantic.dev/capabilities/) for [Pydantic AI](https://ai.pydantic.dev/) agents. Drop them into any agent for cost control, tool permissions, prompt-injection defense, PII detection, and secret redaction — no wrappers, no plumbing.

## Installation

```bash
pip install pydantic-ai-shields
```

## Quick Start

```python
from pydantic_ai import Agent
from pydantic_ai_shields import CostTracking, ToolGuard, InputGuard

agent = Agent(
    "openai:gpt-4.1",
    capabilities=[
        CostTracking(budget_usd=5.0),
        ToolGuard(blocked=["execute"], require_approval=["write_file"]),
        InputGuard(guard=lambda prompt: "ignore all instructions" not in prompt.lower()),
    ],
)

result = await agent.run("Hello!")
```

## Available Shields

### CostTracking

Track token usage and API costs with optional budget enforcement:

```python
from pydantic_ai_shields import CostTracking

tracking = CostTracking(budget_usd=10.0)
agent = Agent("openai:gpt-4.1", capabilities=[tracking])

result = await agent.run("Hello")
print(f"Total cost: ${tracking.total_cost:.4f}")
print(f"Total tokens: {tracking.total_request_tokens + tracking.total_response_tokens}")
```

Raises `BudgetExceededError` when the cumulative cost exceeds the budget. Pricing auto-detected from model via [genai-prices](https://pypi.org/project/genai-prices/).

### ToolGuard

Control which tools the agent can use:

```python
from pydantic_ai_shields import ToolGuard

async def ask_user(tool_name: str, args: dict) -> bool:
    return input(f"Allow {tool_name}? (y/n) ") == "y"

guard = ToolGuard(
    blocked=["execute", "rm"],              # Hidden from model entirely
    require_approval=["write_file"],        # User must approve each call
    approval_callback=ask_user,
)
agent = Agent("openai:gpt-4.1", capabilities=[guard])
```

- **`blocked`** tools are removed via `prepare_tools` — the model never sees them
- **`require_approval`** tools trigger the callback before execution

### InputGuard

Block or validate user input before the agent runs:

```python
from pydantic_ai_shields import InputGuard

# Sync guard
agent = Agent("openai:gpt-4.1", capabilities=[
    InputGuard(guard=lambda prompt: "jailbreak" not in prompt.lower()),
])

# Async guard (e.g., call moderation API)
async def check_toxicity(prompt: str) -> bool:
    result = await moderation_api.check(prompt)
    return result.is_safe

agent = Agent("openai:gpt-4.1", capabilities=[InputGuard(guard=check_toxicity)])
```

Raises `InputBlocked` when the guard returns `False`.

### OutputGuard

Block or validate model output after the agent runs:

```python
from pydantic_ai_shields import OutputGuard

agent = Agent("openai:gpt-4.1", capabilities=[
    OutputGuard(guard=lambda output: "SSN" not in output),
])
```

Raises `OutputBlocked` when the guard returns `False`.

### AsyncGuardrail

Run a guardrail concurrently with the LLM call — if the guard fails first, the LLM is cancelled (saves cost):

```python
from pydantic_ai_shields import AsyncGuardrail, InputGuard

agent = Agent(
    "openai:gpt-4.1",
    capabilities=[AsyncGuardrail(
        guard=InputGuard(guard=check_policy),
        timing="concurrent",       # "concurrent" | "blocking" | "monitoring"
        cancel_on_failure=True,     # Cancel LLM if guard fails
        timeout=5.0,                # Guard timeout in seconds
    )],
)
```

| Timing | Behavior |
|--------|----------|
| `"concurrent"` | Guard runs alongside LLM, fail-fast on violation |
| `"blocking"` | Guard completes before LLM starts (traditional) |
| `"monitoring"` | Guard runs after LLM, fire-and-forget (logging/audit) |

## Built-in Content Shields

### PromptInjection

Detect and block prompt injection / jailbreak attempts:

```python
from pydantic_ai_shields import PromptInjection

agent = Agent("openai:gpt-4.1", capabilities=[
    PromptInjection(sensitivity="high"),  # "low" | "medium" | "high"
])
```

6 detection categories: ignore_instructions, system_override, role_play, delimiter_injection, prompt_leaking, jailbreak. Add custom patterns with `custom_patterns=[r"my_pattern"]`.

### PiiDetector

Detect PII (email, phone, SSN, credit card, IP) in user input:

```python
from pydantic_ai_shields import PiiDetector

agent = Agent("openai:gpt-4.1", capabilities=[
    PiiDetector(detect=["email", "ssn", "credit_card"]),
])
```

Use `action="log"` to allow through while recording detections in `cap.last_detections`.

### SecretRedaction

Block API keys, tokens, and credentials from appearing in model output:

```python
from pydantic_ai_shields import SecretRedaction

agent = Agent("openai:gpt-4.1", capabilities=[SecretRedaction()])
```

Detects: OpenAI, Anthropic, AWS, GitHub, Slack keys, JWTs, private keys, generic API keys.

### BlockedKeywords

Block prompts containing forbidden words or phrases:

```python
from pydantic_ai_shields import BlockedKeywords

agent = Agent("openai:gpt-4.1", capabilities=[
    BlockedKeywords(
        keywords=["competitor_name", "internal_only"],
        whole_words=True,
    ),
])
```

Supports `case_sensitive`, `whole_words`, and `use_regex` modes.

### NoRefusals

Block LLM refusals — ensure the model attempts to answer:

```python
from pydantic_ai_shields import NoRefusals

agent = Agent("openai:gpt-4.1", capabilities=[NoRefusals()])
```

Use `allow_partial=True` to allow responses that contain refusal language but also have substance.

## Composing Shields

All shields compose naturally as pydantic-ai capabilities:

```python
agent = Agent(
    "openai:gpt-4.1",
    capabilities=[
        CostTracking(budget_usd=5.0),
        PromptInjection(sensitivity="high"),
        PiiDetector(),
        SecretRedaction(),
        BlockedKeywords(keywords=["classified"]),
        NoRefusals(),
    ],
)
```

## API Reference

### Infrastructure Shields

| Class | Description |
|-------|-------------|
| `CostTracking` | Token/USD tracking with budget enforcement |
| `ToolGuard` | Block tools or require approval |
| `InputGuard` | Custom input validation (pluggable function) |
| `OutputGuard` | Custom output validation (pluggable function) |
| `AsyncGuardrail` | Concurrent guardrail + LLM execution |

### Content Shields

| Class | Description |
|-------|-------------|
| `PromptInjection` | Detect prompt injection / jailbreak (6 categories, 3 sensitivity levels) |
| `PiiDetector` | Detect PII — email, phone, SSN, credit card, IP (regex-based) |
| `SecretRedaction` | Block API keys, tokens, credentials in output |
| `BlockedKeywords` | Block forbidden keywords/phrases (case, word boundary, regex modes) |
| `NoRefusals` | Block LLM refusals ("I cannot help with that") |

### Data

| Class | Description |
|-------|-------------|
| `CostInfo` | Per-run and cumulative token/cost data |

### Exceptions

| Exception | Raised by |
|-----------|-----------|
| `GuardrailError` | Base exception for all shields |
| `InputBlocked` | `InputGuard`, `PromptInjection`, `PiiDetector`, `BlockedKeywords`, `AsyncGuardrail` |
| `OutputBlocked` | `OutputGuard`, `SecretRedaction`, `NoRefusals` |
| `ToolBlocked` | `ToolGuard` |
| `BudgetExceededError` | `CostTracking` |

## Vstorm OSS Ecosystem

This library is one piece of a broader open-source toolkit for production AI agents — all built on **[Pydantic AI](https://github.com/pydantic/pydantic-ai)**.

| Project | Description | Stars |
|---------|-------------|:-----:|
| **[Pydantic Deep Agents](https://github.com/vstorm-co/pydantic-deepagents)** | The full agent framework **and** terminal assistant — bundles every library below into one `create_deep_agent()` call. | [![Stars](https://img.shields.io/github/stars/vstorm-co/pydantic-deepagents?style=flat&logo=github&color=yellow)](https://github.com/vstorm-co/pydantic-deepagents) |
| **[pydantic-ai-backend](https://github.com/vstorm-co/pydantic-ai-backend)** | Sandboxed execution & file tools — State / Local / Docker / Daytona backends + console toolset. | [![Stars](https://img.shields.io/github/stars/vstorm-co/pydantic-ai-backend?style=flat&logo=github&color=yellow)](https://github.com/vstorm-co/pydantic-ai-backend) |
| **[subagents-pydantic-ai](https://github.com/vstorm-co/subagents-pydantic-ai)** | Declarative multi-agent orchestration — sync / async / auto, with token tracking. | [![Stars](https://img.shields.io/github/stars/vstorm-co/subagents-pydantic-ai?style=flat&logo=github&color=yellow)](https://github.com/vstorm-co/subagents-pydantic-ai) |
| **[summarization-pydantic-ai](https://github.com/vstorm-co/summarization-pydantic-ai)** | Unlimited context for long-running agents — summarization or sliding window. | [![Stars](https://img.shields.io/github/stars/vstorm-co/summarization-pydantic-ai?style=flat&logo=github&color=yellow)](https://github.com/vstorm-co/summarization-pydantic-ai) |
| 👉 **[pydantic-ai-shields](https://github.com/vstorm-co/pydantic-ai-shields)** | Drop-in guardrails — cost caps, prompt-injection defense, PII & secret redaction, tool blocking. | [![Stars](https://img.shields.io/github/stars/vstorm-co/pydantic-ai-shields?style=flat&logo=github&color=yellow)](https://github.com/vstorm-co/pydantic-ai-shields) |
| **[pydantic-ai-todo](https://github.com/vstorm-co/pydantic-ai-todo)** | Task planning with subtasks, dependencies, and cycle detection. | [![Stars](https://img.shields.io/github/stars/vstorm-co/pydantic-ai-todo?style=flat&logo=github&color=yellow)](https://github.com/vstorm-co/pydantic-ai-todo) |
| **[full-stack-ai-agent-template](https://github.com/vstorm-co/full-stack-ai-agent-template)** | Zero to production AI app in 30 minutes — FastAPI + Next.js 15, RAG, 6 AI frameworks. | [![Stars](https://img.shields.io/github/stars/vstorm-co/full-stack-ai-agent-template?style=flat&logo=github&color=yellow)](https://github.com/vstorm-co/full-stack-ai-agent-template) |

> **Want it all wired together?** [Pydantic Deep Agents](https://github.com/vstorm-co/pydantic-deepagents) ships every library above integrated — planning, filesystem, subagents, memory, context management, and guardrails — behind a single function call. Browse everything at [oss.vstorm.co](https://oss.vstorm.co).


## Contributing

```bash
git clone https://github.com/vstorm-co/pydantic-ai-shields.git
cd pydantic-ai-shields
make install
make test   # 100% coverage required
make all    # lint + typecheck + test
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.


## Star History

If this library saved you from wiring an agent harness by hand — **[give it a ⭐](https://github.com/vstorm-co/pydantic-ai-shields)**. It's the single biggest thing that helps the project grow.

<p align="center">
  <a href="https://www.star-history.com/#vstorm-co/pydantic-ai-shields&type=date">
    <img src="https://api.star-history.com/svg?repos=vstorm-co/pydantic-ai-shields&type=date" alt="Star History" width="600">
  </a>
</p>

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

### Need help shipping AI agents in production?

<p>We're <a href="https://vstorm.co"><b>Vstorm</b></a> — an Applied Agentic AI Engineering Consultancy<br>with 30+ production agent implementations. <a href="https://github.com/vstorm-co/pydantic-deepagents"><b>Pydantic Deep Agents</b></a> is what we build them with.</p>

<a href="https://vstorm.co/contact-us/">
  <img src="https://img.shields.io/badge/Talk%20to%20us%20%E2%86%92-0066FF?style=for-the-badge&logoColor=white" alt="Talk to us">
</a>

<br><br>

Made with **care** by <a href="https://vstorm.co"><b>Vstorm</b></a>

</div>
