# tests/integration/test_calculation.py
"""
Integration tests for the Calculation model against a PostgreSQL database
"""

import uuid

import pytest

from app.models.calculation import Calculation, CalculationType, OperationFactory
from tests.conftest import create_fake_user
from app.models.user import User


def _make_user(db_session):
    user = User(**create_fake_user())
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_insert_and_read_calculation(db_session):
    user = _make_user(db_session)

    calc = Calculation(
        user_id=user.id,
        a=6,
        b=4,
        type=CalculationType.ADD.value,
    )
    calc.result = OperationFactory.compute(CalculationType.ADD, 6, 4)
    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    fetched = db_session.query(Calculation).filter_by(id=calc.id).first()
    assert fetched is not None
    assert fetched.a == 6
    assert fetched.b == 4
    assert fetched.type == "add"
    assert fetched.result == 10
    assert fetched.user_id == user.id


def test_compute_result_helper_persists(db_session):
    user = _make_user(db_session)

    calc = Calculation(
        user_id=user.id, a=20, b=5, type=CalculationType.DIVIDE.value
    )
    calc.compute_result()
    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    assert calc.result == 4


def test_relationship_links_user_and_calculation(db_session):
    user = _make_user(db_session)
    calc = Calculation(
        user_id=user.id, a=3, b=3, type=CalculationType.MULTIPLY.value
    )
    db_session.add(calc)
    db_session.commit()
    db_session.refresh(user)

    assert calc.user.id == user.id
    assert calc in user.calculations


def test_divide_by_zero_raises_before_persist(db_session):
    user = _make_user(db_session)
    calc = Calculation(
        user_id=user.id, a=5, b=0, type=CalculationType.DIVIDE.value
    )
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.compute_result()


def test_calculation_requires_valid_user_fk(db_session):
    orphan = Calculation(
        user_id=uuid.uuid4(),  # no such user
        a=1,
        b=2,
        type=CalculationType.ADD.value,
        result=3,
    )
    db_session.add(orphan)
    with pytest.raises(Exception):  # IntegrityError from the FK constraint
        db_session.commit()
    db_session.rollback()