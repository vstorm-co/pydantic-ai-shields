# Cost Tracking

`CostTracking` tracks token usage and calculates USD costs across agent runs using
[genai-prices](https://pypi.org/project/genai-prices/).

## Basic Usage

```python
from pydantic_ai import Agent
from pydantic_ai_shields import CostTracking

tracking = CostTracking(budget_usd=5.0)
agent = Agent("openai:gpt-4.1", capabilities=[tracking])

result = await agent.run("Hello")

print(f"Cost: ${tracking.total_cost:.4f}")
print(f"Tokens: {tracking.total_request_tokens} in / {tracking.total_response_tokens} out")
print(f"Runs: {tracking.run_count}")
```

## Budget Enforcement

When cumulative cost reaches or exceeds `budget_usd`, a
[`BudgetExceededError`][pydantic_ai_shields.guardrails.BudgetExceededError] is raised:

```python
from pydantic_ai_shields import CostTracking, BudgetExceededError

tracking = CostTracking(budget_usd=1.0)
agent = Agent("openai:gpt-4.1", capabilities=[tracking])

try:
    for i in range(1000):
        await agent.run(f"Query {i}")
except BudgetExceededError as e:
    print(f"Budget exceeded: ${e.total_cost:.4f} > ${e.budget:.4f}")
```

The budget is checked at **two** points:

- In `before_run`, before a run starts — so a run is rejected up front if the
  accumulated cost already meets or exceeds the budget.
- In `after_run`, once the just-completed run's cost has been added — so the
  run that *crosses* the threshold is the one that raises.

This means the run that pushes you over budget still completes (you pay for its
tokens), and the *next* run is blocked before it starts.

## Pricing Failures and Strict Mode

Costs are resolved via [genai-prices](https://pypi.org/project/genai-prices/). If
the model cannot be priced (unknown model, missing pricing data), behavior depends
on the `strict` flag:

- **Default (`strict=False`)** — a warning is logged and the run's cost is treated
  as `None`. `run_cost_usd` (and `total_cost_usd` for that callback) will be `None`,
  and the cost is simply not added to the cumulative total. The run proceeds normally.
- **`strict=True`** — a [`PricingError`][pydantic_ai_shields.guardrails.PricingError]
  is raised, carrying the offending `model_name`.

```python
from pydantic_ai_shields import CostTracking, PricingError

tracking = CostTracking(model_name="some:unknown-model", strict=True)
agent = Agent("some:unknown-model", capabilities=[tracking])

try:
    await agent.run("Hello")
except PricingError as e:
    print(f"Could not price model: {e.model_name}")
```

## Cost Callbacks

The `on_cost_update` callback receives a
[`CostInfo`][pydantic_ai_shields.guardrails.CostInfo] after each run. It may be a
sync or async function.

!!! warning "Cost fields can be `None`"
    When the model cannot be priced (and `strict=False`), `run_cost_usd` and
    `total_cost_usd` are `None`. Always guard against `None` before formatting,
    or you will hit a `TypeError`. The token fields are always populated.

```python
from pydantic_ai_shields import CostTracking, CostInfo

def on_cost(info: CostInfo):
    if info.run_cost_usd is None:
        print(f"Run #{info.run_count}: cost unknown (model not priced)")
    else:
        print(f"Run #{info.run_count}: ${info.run_cost_usd:.4f} (total: ${info.total_cost_usd:.4f})")

agent = Agent("openai:gpt-4.1", capabilities=[CostTracking(on_cost_update=on_cost)])
```

## Auto-Detection

Model pricing is auto-detected from `ctx.model.model_id` on the first run.
You can also specify explicitly:

```python
CostTracking(model_name="openai:gpt-4.1", budget_usd=5.0)
```
