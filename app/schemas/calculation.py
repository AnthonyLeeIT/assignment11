# app/schemas/calculation.py
"""
Pydantic schemas for the Calculation model.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.models.calculation import CalculationType


class CalculationBase(BaseModel):

    a: float
    b: float
    type: CalculationType


class CalculationCreate(CalculationBase):
    """
    Schema for incoming calculation requests.
    """

    user_id: UUID

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value):
        """Accept 'Add', 'ADD', 'add', etc. by lowercasing string input."""
        if isinstance(value, str):
            return value.lower()
        return value

    @model_validator(mode="after")
    def reject_zero_divisor(self):
        """Block division by zero at validation time (LBYL)."""
        if self.type is CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Cannot divide by zero.")
        return self


class CalculationRead(CalculationBase):
    """
    Schema for returning calculation details.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    result: float | None = None
    created_at: datetime
    updated_at: datetime