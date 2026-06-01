# API Reference

Complete API documentation for pydantic-ai-shields.

## Infrastructure Shields

- [`CostTracking`][pydantic_ai_shields.guardrails.CostTracking] — Token/USD tracking with budget enforcement
- [`ToolGuard`][pydantic_ai_shields.guardrails.ToolGuard] — Block tools or require approval
- [`InputGuard`][pydantic_ai_shields.guardrails.InputGuard] — Custom input validation
- [`OutputGuard`][pydantic_ai_shields.guardrails.OutputGuard] — Custom output validation
- [`AsyncGuardrail`][pydantic_ai_shields.guardrails.AsyncGuardrail] — Concurrent guardrail + LLM execution

## Content Shields

- [`PromptInjection`][pydantic_ai_shields.shields.PromptInjection] — Prompt injection / jailbreak detection
- [`PiiDetector`][pydantic_ai_shields.shields.PiiDetector] — PII detection
- [`SecretRedaction`][pydantic_ai_shields.shields.SecretRedaction] — Secret/credential detection in output
- [`BlockedKeywords`][pydantic_ai_shields.shields.BlockedKeywords] — Keyword blocking
- [`NoRefusals`][pydantic_ai_shields.shields.NoRefusals] — Refusal detection

## Data

- [`CostInfo`][pydantic_ai_shields.guardrails.CostInfo] — Token usage and cost data passed to `on_cost_update`

## Exceptions

- [`GuardrailError`][pydantic_ai_shields.guardrails.GuardrailError] — Base exception
- [`InputBlocked`][pydantic_ai_shields.guardrails.InputBlocked] — Input validation failed
- [`OutputBlocked`][pydantic_ai_shields.guardrails.OutputBlocked] — Output validation failed
- [`ToolBlocked`][pydantic_ai_shields.guardrails.ToolBlocked] — Tool access denied
- [`BudgetExceededError`][pydantic_ai_shields.guardrails.BudgetExceededError] — Cost budget exceeded
- [`PricingError`][pydantic_ai_shields.guardrails.PricingError] — Cost calculation failed (strict mode)
