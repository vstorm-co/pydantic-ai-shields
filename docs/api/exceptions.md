# Exceptions

All shield exceptions inherit from [`GuardrailError`][pydantic_ai_shields.guardrails.GuardrailError].

| Exception | Raised by |
|-----------|-----------|
| [`InputBlocked`][pydantic_ai_shields.guardrails.InputBlocked] | `InputGuard`, `PromptInjection`, `PiiDetector`, `BlockedKeywords` |
| [`OutputBlocked`][pydantic_ai_shields.guardrails.OutputBlocked] | `OutputGuard`, `SecretRedaction`, `NoRefusals` |
| [`ToolBlocked`][pydantic_ai_shields.guardrails.ToolBlocked] | `ToolGuard` |
| [`BudgetExceededError`][pydantic_ai_shields.guardrails.BudgetExceededError] | `CostTracking` |
| [`PricingError`][pydantic_ai_shields.guardrails.PricingError] | `CostTracking(strict=True)` |

::: pydantic_ai_shields.guardrails
    options:
      show_root_heading: false
      show_source: true
      members:
        - GuardrailError
        - InputBlocked
        - OutputBlocked
        - ToolBlocked
        - BudgetExceededError
        - PricingError
