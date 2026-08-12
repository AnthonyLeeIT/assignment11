# app/models/calculation.py
"""
Calculation model.

A single-table SQLAlchemy model representing one arithmetic calculation
performed by a user.
"""

from datetime import datetime
import enum
import uuid

from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class CalculationType(str, enum.Enum):

    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class OperationFactory:

    _operations = {
        CalculationType.ADD: lambda a, b: a + b,
        CalculationType.SUBTRACT: lambda a, b: a - b,
        CalculationType.MULTIPLY: lambda a, b: a * b,
        CalculationType.DIVIDE: lambda a, b: a / b,
    }

    @classmethod
    def compute(cls, calc_type: "CalculationType", a: float, b: float) -> float:
        """
        Args:
            calc_type: The operation type
            a: First operand
            b: Second operand

        Returns:
            The result of the operation as float

        Raises:
            ValueError: If type is unknown, or on division by zero.
        """
        operation = cls._operations.get(calc_type)
        if operation is None:
            raise ValueError(f"Unsupported calculation type: {calc_type}")
        if calc_type is CalculationType.DIVIDE and b == 0:
            raise ValueError("Cannot divide by zero.")
        return float(operation(a, b))


class Calculation(Base):

    __tablename__ = "calculations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)
    result = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="calculations")

    def compute_result(self) -> float:
        self.result = OperationFactory.compute(
            CalculationType(self.type), self.a, self.b
        )
        return self.result

    def __repr__(self):
        return (
            f"<Calculation(type={self.type}, a={self.a}, "
            f"b={self.b}, result={self.result})>"
        )
