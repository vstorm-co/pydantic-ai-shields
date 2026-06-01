"""Tests for guardrail capabilities."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic_ai.tools import ToolDefinition

from pydantic_ai_shields.guardrails import (
    AsyncGuardrail,
    BudgetExceededError,
    CostInfo,
    CostTracking,
    GuardrailError,
    InputBlocked,
    InputGuard,
    OutputBlocked,
    OutputGuard,
    PricingError,
    ToolBlocked,
    ToolGuard,
)
from unittest.mock import patch
from decimal import Decimal
from unittest.mock import MagicMock, patch
import asyncio
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from pydantic_ai.messages import ToolCallPart

# ---------------------------------------------------------------------------
# CostTracking
# ---------------------------------------------------------------------------


class TestCostTracking:
    def test_default_construction(self):
        cap = CostTracking()
        assert cap.budget_usd is None
        assert cap.total_cost == 0.0
        assert cap.run_count == 0

    @pytest.mark.anyio
    async def test_tracks_tokens(self):
        cap = CostTracking()
        agent = Agent(TestModel(), capabilities=[cap])
        await agent.run("Hello")
        assert cap.run_count == 1
        assert cap.total_request_tokens >= 0
        assert cap.total_response_tokens >= 0

    @pytest.mark.anyio
    async def test_callback_called(self):
        infos: list[CostInfo] = []
        cap = CostTracking(on_cost_update=lambda info: infos.append(info))
        agent = Agent(TestModel(), capabilities=[cap])
        await agent.run("Hello")
        assert len(infos) == 1
        assert infos[0].run_count == 1

    @pytest.mark.anyio
    async def test_async_callback(self):
        infos: list[CostInfo] = []

        async def cb(info: CostInfo) -> None:
            infos.append(info)

        cap = CostTracking(on_cost_update=cb)
        agent = Agent(TestModel(), capabilities=[cap])
        await agent.run("Hello")
        assert len(infos) == 1

    @pytest.mark.anyio
    async def test_multiple_runs_accumulate(self):
        cap = CostTracking()
        agent = Agent(TestModel(), capabilities=[cap])
        await agent.run("One")
        await agent.run("Two")
        assert cap.run_count == 2

    @pytest.mark.anyio
    async def test_budget_exceeded(self):
        cap = CostTracking(budget_usd=0.0)  # Zero budget
        agent = Agent(TestModel(), capabilities=[cap])
        # First run won't fail (budget checked before run, starts at 0)
        # Set cost artificially to trigger on next run
        cap._total_cost_usd = 1.0
        with pytest.raises(BudgetExceededError):
            await agent.run("Hello")

    @pytest.mark.anyio
    async def test_cost_accumulates_when_prices_resolve(self):
        """Cost accumulates in total_cost_usd when _calculate_cost returns a value."""

        cap = CostTracking()
        agent = Agent(TestModel(), capabilities=[cap])

        with patch.object(cap, "_calculate_cost", return_value=0.005):
            await agent.run("Hello")

        assert cap.total_cost == 0.005


# ---------------------------------------------------------------------------
# ToolGuard
# ---------------------------------------------------------------------------


class TestToolGuard:
    def test_default_construction(self):
        cap = ToolGuard()
        assert cap.blocked == []
        assert cap.require_approval == []

    @pytest.mark.anyio
    async def test_agent_runs_with_guard(self):
        cap = ToolGuard(blocked=["execute"])
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("Hello")
        assert result.output is not None

    @pytest.mark.anyio
    async def test_no_blocked_returns_all(self):
        """No blocked tools → all tools returned."""
        cap = ToolGuard()
        ctx = _make_ctx()
        tool_defs = [
            ToolDefinition(name="read_file", description="read"),
            ToolDefinition(name="execute", description="exec"),
        ]
        result = await cap.prepare_tools(ctx, tool_defs)
        assert len(result) == 2

    @pytest.mark.anyio
    async def test_blocked_tools_hidden(self):
        cap = ToolGuard(blocked=["execute", "write_file"])

        ctx = _make_ctx()

        tool_defs = [
            ToolDefinition(name="read_file", description="read"),
            ToolDefinition(name="execute", description="exec"),
            ToolDefinition(name="write_file", description="write"),
        ]

        result = await cap.prepare_tools(ctx, tool_defs)
        names = [td.name for td in result]
        assert "read_file" in names
        assert "execute" not in names
        assert "write_file" not in names

    @pytest.mark.anyio
    async def test_approval_granted(self):
        async def approve(tool_name: str, args: dict[str, Any]) -> bool:
            return True

        cap = ToolGuard(require_approval=["write_file"], approval_callback=approve)
        ctx = _make_ctx()
        call = _make_call("write_file")
        tool_def = ToolDefinition(name="write_file", description="write")

        result = await cap.before_tool_execute(
            ctx, call=call, tool_def=tool_def, args={"path": "/test"}
        )
        assert result == {"path": "/test"}

    @pytest.mark.anyio
    async def test_approval_denied(self):
        async def deny(tool_name: str, args: dict[str, Any]) -> bool:
            return False

        cap = ToolGuard(require_approval=["write_file"], approval_callback=deny)
        ctx = _make_ctx()
        call = _make_call("write_file")
        tool_def = ToolDefinition(name="write_file", description="write")

        with pytest.raises(ToolBlocked, match="User denied"):
            await cap.before_tool_execute(ctx, call=call, tool_def=tool_def, args={"path": "/test"})

    @pytest.mark.anyio
    async def test_approval_no_callback_raises(self):
        cap = ToolGuard(require_approval=["write_file"])
        ctx = _make_ctx()
        call = _make_call("write_file")
        tool_def = ToolDefinition(name="write_file", description="write")

        with pytest.raises(ToolBlocked, match="no callback"):
            await cap.before_tool_execute(ctx, call=call, tool_def=tool_def, args={})

    @pytest.mark.anyio
    async def test_non_guarded_tool_passes_through(self):
        cap = ToolGuard(require_approval=["write_file"])
        ctx = _make_ctx()
        call = _make_call("read_file")
        tool_def = ToolDefinition(name="read_file", description="read")

        result = await cap.before_tool_execute(
            ctx, call=call, tool_def=tool_def, args={"path": "/test"}
        )
        assert result == {"path": "/test"}

    @pytest.mark.anyio
    async def test_sync_approval_callback(self):
        def approve_sync(tool_name: str, args: dict[str, Any]) -> bool:
            return True

        cap = ToolGuard(require_approval=["write_file"], approval_callback=approve_sync)
        ctx = _make_ctx()
        call = _make_call("write_file")
        tool_def = ToolDefinition(name="write_file", description="write")

        result = await cap.before_tool_execute(
            ctx, call=call, tool_def=tool_def, args={"path": "/test"}
        )
        assert result == {"path": "/test"}


# ---------------------------------------------------------------------------
# InputGuard
# ---------------------------------------------------------------------------


class TestInputGuard:
    @pytest.mark.anyio
    async def test_safe_input_passes(self):
        cap = InputGuard(guard=lambda prompt: True)
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("Hello")
        assert result.output is not None

    @pytest.mark.anyio
    async def test_unsafe_input_blocked(self):
        cap = InputGuard(guard=lambda prompt: False)
        agent = Agent(TestModel(), capabilities=[cap])
        with pytest.raises(InputBlocked):
            await agent.run("Bad input")

    @pytest.mark.anyio
    async def test_async_guard(self):
        async def check(prompt: str) -> bool:
            return "safe" in prompt

        cap = InputGuard(guard=check)
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("This is safe")
        assert result.output is not None

    @pytest.mark.anyio
    async def test_no_guard_passes(self):
        cap = InputGuard()
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("Hello")
        assert result.output is not None


# ---------------------------------------------------------------------------
# OutputGuard
# ---------------------------------------------------------------------------


class TestOutputGuard:
    @pytest.mark.anyio
    async def test_safe_output_passes(self):
        cap = OutputGuard(guard=lambda output: True)
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("Hello")
        assert result.output is not None

    @pytest.mark.anyio
    async def test_unsafe_output_blocked(self):
        cap = OutputGuard(guard=lambda output: False)
        agent = Agent(TestModel(), capabilities=[cap])
        with pytest.raises(OutputBlocked):
            await agent.run("Hello")

    @pytest.mark.anyio
    async def test_async_guard(self):
        """Async output guard is awaited."""

        async def check(output: str) -> bool:
            return True

        cap = OutputGuard(guard=check)
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("Hello")
        assert result.output is not None

    @pytest.mark.anyio
    async def test_no_guard_passes(self):
        cap = OutputGuard()
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("Hello")
        assert result.output is not None


# ---------------------------------------------------------------------------
# AsyncGuardrail
# ---------------------------------------------------------------------------


class TestAsyncGuardrail:
    @pytest.mark.anyio
    async def test_blocking_mode(self):
        cap = AsyncGuardrail(
            guard=InputGuard(guard=lambda p: True),
            timing="blocking",
        )
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("Hello")
        assert result.output is not None

    @pytest.mark.anyio
    async def test_concurrent_mode_passes(self):
        cap = AsyncGuardrail(
            guard=InputGuard(guard=lambda p: True),
            timing="concurrent",
        )
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("Hello")
        assert result.output is not None

    @pytest.mark.anyio
    async def test_concurrent_mode_fails(self):
        cap = AsyncGuardrail(
            guard=InputGuard(guard=lambda p: False),
            timing="concurrent",
            cancel_on_failure=True,
        )
        agent = Agent(TestModel(), capabilities=[cap])
        with pytest.raises(InputBlocked):
            await agent.run("Bad input")

    @pytest.mark.anyio
    async def test_monitoring_mode(self):
        cap = AsyncGuardrail(
            guard=InputGuard(guard=lambda p: True),
            timing="monitoring",
        )
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("Hello")
        assert result.output is not None

    @pytest.mark.anyio
    async def test_no_guard(self):
        cap = AsyncGuardrail(timing="concurrent")
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("Hello")
        assert result.output is not None


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------


class TestComposition:
    @pytest.mark.anyio
    async def test_multiple_guardrails(self):
        agent = Agent(
            TestModel(),
            capabilities=[
                CostTracking(),
                InputGuard(guard=lambda p: True),
                OutputGuard(guard=lambda o: True),
                ToolGuard(blocked=["execute"]),
            ],
        )
        result = await agent.run("Hello")
        assert result.output is not None


# ---------------------------------------------------------------------------
# CostTracking pricing
# ---------------------------------------------------------------------------


class TestCostTrackingPricing:
    def test_calculate_cost_with_provider_prefix(self):
        """Cost calculation with 'provider:model' format."""

        cap = CostTracking()
        mock_result = MagicMock()
        mock_result.total_price = Decimal("0.002")
        with patch("genai_prices.calc_price", return_value=mock_result) as mock_calc:
            cost = cap._calculate_cost("openai:gpt-4.1", 1000, 500)
        assert cost == 0.002
        call_kwargs = mock_calc.call_args
        assert call_kwargs.kwargs["model_ref"] == "gpt-4.1"
        assert call_kwargs.kwargs["provider_id"] == "openai"

    def test_calculate_cost_plain_model(self):
        """Cost calculation with plain model name (no provider prefix)."""

        cap = CostTracking()
        mock_result = MagicMock()
        mock_result.total_price = Decimal("0.001")
        with patch("genai_prices.calc_price", return_value=mock_result) as mock_calc:
            cost = cap._calculate_cost("gpt-4.1", 1000, 500)
        assert cost == 0.001
        call_kwargs = mock_calc.call_args
        assert call_kwargs.kwargs["model_ref"] == "gpt-4.1"
        assert call_kwargs.kwargs["provider_id"] is None

    def test_calculate_cost_failure_returns_none(self):
        """Cost calculation returns None with warning on failure (non-strict)."""

        cap = CostTracking()
        with patch("genai_prices.calc_price", side_effect=Exception("unknown model")):
            cost = cap._calculate_cost("unknown:model", 1000, 500)
        assert cost is None

    def test_calculate_cost_strict_raises_pricing_error(self):
        """Cost calculation raises PricingError in strict mode."""

        cap = CostTracking(strict=True)
        with (
            patch("genai_prices.calc_price", side_effect=Exception("unknown model")),
            pytest.raises(PricingError, match="unknown:model"),
        ):
            cap._calculate_cost("unknown:model", 1000, 500)

    @pytest.mark.anyio
    async def test_after_run_skips_cost_when_no_model_name(self):
        """_calculate_cost is never called when model_id is falsy and model_name is None."""

        class _NoIdModel(TestModel):
            model_id = None  # type: ignore[assignment]

        cap = CostTracking()  # model_name=None
        agent = Agent(_NoIdModel(), capabilities=[cap])

        with patch.object(cap, "_calculate_cost") as mock_calc:
            await agent.run("Hello")

        mock_calc.assert_not_called()
        assert cap.total_cost == 0.0
        assert cap.run_count == 1


# ---------------------------------------------------------------------------
# Exception messages
# ---------------------------------------------------------------------------


class TestExceptions:
    def test_tool_blocked_with_reason(self):
        err = ToolBlocked("execute", "dangerous")
        assert "execute" in str(err)
        assert "dangerous" in str(err)

    def test_tool_blocked_without_reason(self):
        err = ToolBlocked("execute")
        assert "execute" in str(err)

    def test_budget_exceeded(self):
        err = BudgetExceededError(5.50, 5.00)
        assert err.total_cost == 5.50
        assert err.budget == 5.00

    def test_guardrail_error_base(self):
        err = GuardrailError("test")
        assert str(err) == "test"

    def test_pricing_error(self):
        err = PricingError("openai:future-model")
        assert err.model_name == "openai:future-model"
        assert "openai:future-model" in str(err)
        assert isinstance(err, GuardrailError)


# ---------------------------------------------------------------------------
# AsyncGuardrail edge cases
# ---------------------------------------------------------------------------


class TestAsyncGuardrailEdgeCases:
    @pytest.mark.anyio
    async def test_concurrent_guard_failure_no_cancel(self):
        """Concurrent mode with cancel_on_failure=False logs but doesn't raise."""
        cap = AsyncGuardrail(
            guard=InputGuard(guard=lambda p: False),
            timing="concurrent",
            cancel_on_failure=False,
        )
        agent = Agent(TestModel(), capabilities=[cap])
        result = await agent.run("Should pass despite guard failure")
        assert result.output is not None

    @pytest.mark.anyio
    async def test_timeout_on_guard(self):
        """Guard timeout is handled."""

        async def slow_guard(prompt: str) -> bool:
            await asyncio.sleep(10)
            return True

        cap = AsyncGuardrail(
            guard=InputGuard(guard=slow_guard),
            timing="concurrent",
            timeout=0.01,
        )
        agent = Agent(TestModel(), capabilities=[cap])
        # Should complete — timeout is logged but doesn't crash
        result = await agent.run("Hello")
        assert result.output is not None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ctx() -> Any:
    return RunContext(deps=None, model=TestModel(), usage=RunUsage())


def _make_call(tool_name: str) -> Any:
    return ToolCallPart(tool_name=tool_name, args={}, tool_call_id="test_call")
