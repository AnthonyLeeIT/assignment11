# tests/unit/test_calculation.py
"""
Unit tests for the Calculation factory and Pydantic schemas.
"""

import uuid

import pytest
from pydantic import ValidationError

from app.models.calculation import CalculationType, OperationFactory
from app.schemas.calculation import CalculationCreate


# ---------------------------------------------------------------------------
# OperationFactory: each operation computes correctly
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "calc_type, a, b, expected",
    [
        (CalculationType.ADD, 2, 3, 5),
        (CalculationType.ADD, -4, 1.5, -2.5),
        (CalculationType.SUBTRACT, 10, 4, 6),
        (CalculationType.SUBTRACT, 0, 7, -7),
        (CalculationType.MULTIPLY, 6, 7, 42),
        (CalculationType.MULTIPLY, -3, 3, -9),
        (CalculationType.DIVIDE, 20, 4, 5),
        (CalculationType.DIVIDE, 9, 2, 4.5),
    ],
)
def test_factory_computes_each_operation(calc_type, a, b, expected):
    assert OperationFactory.compute(calc_type, a, b) == expected


def test_factory_result_is_float():
    assert isinstance(OperationFactory.compute(CalculationType.ADD, 2, 2), float)


def test_factory_divide_by_zero_raises():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        OperationFactory.compute(CalculationType.DIVIDE, 5, 0)


def test_factory_unknown_type_raises():
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        OperationFactory.compute("modulo", 5, 2)


# ---------------------------------------------------------------------------
# CalculationCreate: schema validation
# ---------------------------------------------------------------------------

def test_create_valid_input():
    payload = CalculationCreate(
        a=4, b=2, type="add", user_id=uuid.uuid4()
    )
    assert payload.type is CalculationType.ADD
    assert payload.a == 4
    assert payload.b == 2


def test_create_normalizes_type_case():
    payload = CalculationCreate(
        a=10, b=5, type="Divide", user_id=uuid.uuid4()
    )
    assert payload.type is CalculationType.DIVIDE


def test_create_rejects_invalid_type():
    with pytest.raises(ValidationError):
        CalculationCreate(a=1, b=1, type="power", user_id=uuid.uuid4())


def test_create_rejects_zero_divisor():
    with pytest.raises(ValidationError, match="Cannot divide by zero"):
        CalculationCreate(a=8, b=0, type="divide", user_id=uuid.uuid4())


def test_create_allows_zero_divisor_for_non_division():
    payload = CalculationCreate(
        a=8, b=0, type="add", user_id=uuid.uuid4()
    )
    assert payload.b == 0
