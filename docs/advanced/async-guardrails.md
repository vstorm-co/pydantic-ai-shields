# Async Guardrails

[`AsyncGuardrail`][pydantic_ai_shields.guardrails.AsyncGuardrail] runs a guard
concurrently with the LLM call — if the guard fails first, the LLM is cancelled to
save cost.

!!! note "The guard must be a capability"
    `AsyncGuardrail.guard` expects an `AbstractCapability` (for example an
    [`InputGuard`][pydantic_ai_shields.guardrails.InputGuard]), **not** a bare
    function. `AsyncGuardrail` drives it by calling the guard's `before_run` hook.
    To wrap a plain check function, pass `InputGuard(guard=your_func)`.

## Timing Modes

| Mode | Behavior |
|------|----------|
| `"concurrent"` | Guard runs alongside LLM. If guard fails, LLM result is discarded. |
| `"blocking"` | Guard completes before LLM starts (traditional). |
| `"monitoring"` | LLM runs first, guard runs after (fire-and-forget for audit/logging). |

## Concurrent Mode (Default)

```python
from pydantic_ai import Agent
from pydantic_ai_shields import AsyncGuardrail, InputGuard

async def check_policy(prompt: str) -> bool:
    # Call your policy API
    return await policy_api.check(prompt)

agent = Agent(
    "openai:gpt-4.1",
    capabilities=[AsyncGuardrail(
        guard=InputGuard(guard=check_policy),
        timing="concurrent",
        cancel_on_failure=True,
        timeout=5.0,
    )],
)
```

If `check_policy` returns `False` before the model finishes, the result is discarded
and [`InputBlocked`][pydantic_ai_shields.guardrails.InputBlocked] is raised — no
tokens wasted.

### `cancel_on_failure` and `timeout`

Both `cancel_on_failure` and `timeout` apply **only** to concurrent mode:

- **`cancel_on_failure`** (default `True`) — when the guard fails, the LLM result
  is rejected and `InputBlocked` is raised. Set it to `False` to keep the result
  and merely log the failure. This flag is ignored in `blocking` and `monitoring`
  modes.
- **`timeout`** — the maximum time to wait for the guard *after* the model finishes.
  If the guard is still running and exceeds the timeout, it is cancelled, a warning
  is logged, and the run is **not** blocked on that guard. With no timeout, the run
  waits for the guard to complete.

## Blocking Mode

Traditional sequential execution — guard completes before model starts:

```python
AsyncGuardrail(
    guard=InputGuard(guard=check_policy),
    timing="blocking",
)
```

## Monitoring Mode

Fire-and-forget — the model runs first, then the guard is launched as a detached
background task for logging/audit:

```python
AsyncGuardrail(
    guard=InputGuard(guard=log_for_compliance),
    timing="monitoring",
)
```

!!! warning "Monitoring never blocks and swallows errors"
    In monitoring mode the result is returned immediately and the guard runs in a
    background task. Any exception the guard raises is **caught and logged** (at
    debug level) — it never propagates, never blocks the run, and never raises
    `InputBlocked`. `cancel_on_failure` and `timeout` have no effect here. Use this
    mode strictly for observation, not enforcement.

## Combining with Other Shields

```python
agent = Agent(
    "openai:gpt-4.1",
    capabilities=[
        PromptInjection(),                    # Fast regex check (before_run)
        AsyncGuardrail(                       # Slow API check (concurrent with LLM)
            guard=InputGuard(guard=external_moderation_api),
            timing="concurrent",
        ),
        SecretRedaction(),                    # Output check (after_run)
    ],
)
```
