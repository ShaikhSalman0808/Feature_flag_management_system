import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.base import Base
from app.database.session import SessionLocal
from app.models.environment import Environment
from app.models.flag import Flag
from app.services.evaluation_engine import evaluate_flag


@pytest.fixture
def db_session():
    """Fixture to create an in-memory SQLite database session for isolated testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def print_sql_table_results(db):
    """Evaluates sample flags against the database and prints results formatted like an SQL query table."""
    test_cases = [
        ("new_checkout_flow", "Production"),
        ("dark_mode_theme", "Development"),
        ("ai_recommendations", "Staging"),
        ("beta_search_engine", "QA"),
        ("payment_gateway_v3", "Sandbox"),
        ("non_existent_flag", "Production"),
        ("new_checkout_flow", "NonExistentEnv"),
    ]

    results = []
    for flag_key, env_name in test_cases:
        res = evaluate_flag(db, flag_key, env_name)
        results.append({
            "flag_key": flag_key,
            "environment": env_name,
            "success": str(res.get("success")),
            "enabled": str(res.get("enabled", "N/A")),
            "value": str(res.get("value", "N/A")),
            "message": res.get("message", "OK"),
        })

    # Format into ASCII SQL Table
    headers = ["FLAG KEY", "ENVIRONMENT", "ENABLED", "VALUE", "SUCCESS", "MESSAGE"]
    col_widths = {
        "FLAG KEY": max(len(r["flag_key"]) for r in results) + 2,
        "ENVIRONMENT": max(len(r["environment"]) for r in results) + 2,
        "ENABLED": 9,
        "VALUE": max(len(r["value"]) for r in results) + 2,
        "SUCCESS": 9,
        "MESSAGE": max(len(r["message"]) for r in results) + 2,
    }

    def print_row(cols):
        line = "|"
        for head, val in zip(headers, cols):
            line += f" {val:<{col_widths[head] - 1}}|"
        print(line)

    separator = "+" + "+".join("-" * col_widths[h] for h in headers) + "+"

    print("\n" + "=" * 85)
    print("                     EVALUATION ENGINE RESULTS (SQL VIEW)                    ")
    print("=" * 85)
    print(separator)
    print_row(headers)
    print(separator)

    for r in results:
        print_row([r["flag_key"], r["environment"], r["enabled"], r["value"], r["success"], r["message"]])

    print(separator)
    print(f"({len(results)} rows evaluated successfully)\n")


# --- Pytest Unit Tests ---

def test_evaluate_flag_environment_not_found(db_session):
    """Test evaluating a flag when the environment does not exist."""
    result = evaluate_flag(
        db=db_session,
        flag_key="new_feature",
        environment_name="non_existent_env",
    )
    assert result["success"] is False
    assert result["message"] == "Environment not found"


def test_evaluate_flag_not_found(db_session):
    """Test evaluating a non-existent flag in a valid environment."""
    env = Environment(name="production", description="Production environment")
    db_session.add(env)
    db_session.commit()

    result = evaluate_flag(
        db=db_session,
        flag_key="unknown_flag",
        environment_name="production",
    )
    assert result["success"] is False
    assert result["message"] == "Feature flag not found"


def test_evaluate_flag_enabled(db_session):
    """Test evaluating an enabled feature flag."""
    env = Environment(name="production", description="Production environment")
    db_session.add(env)
    db_session.commit()

    flag = Flag(
        name="New Checkout Flow",
        key="new_checkout",
        description="Enables the new checkout UI",
        is_enabled=True,
        environment_id=env.id,
        default_value="v2",
    )
    db_session.add(flag)
    db_session.commit()

    result = evaluate_flag(
        db=db_session,
        flag_key="new_checkout",
        environment_name="production",
    )
    assert result["success"] is True
    assert result["flag"] == "new_checkout"
    assert result["enabled"] is True
    assert result["value"] == "v2"


def test_evaluate_flag_disabled(db_session):
    """Test evaluating a disabled feature flag."""
    env = Environment(name="staging", description="Staging environment")
    db_session.add(env)
    db_session.commit()

    flag = Flag(
        name="Beta Search Engine",
        key="beta_search",
        description="Enables elasticsearch backend",
        is_enabled=False,
        environment_id=env.id,
        default_value="standard",
    )
    db_session.add(flag)
    db_session.commit()

    result = evaluate_flag(
        db=db_session,
        flag_key="beta_search",
        environment_name="staging",
    )
    assert result["success"] is True
    assert result["flag"] == "beta_search"
    assert result["enabled"] is False
    assert result["value"] == "standard"


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print_sql_table_results(db)
    finally:
        db.close()
