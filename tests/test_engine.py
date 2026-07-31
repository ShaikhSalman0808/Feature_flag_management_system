import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import SessionLocal
from app.services.evaluation_engine import evaluate_flag


def test_default_value_fallback():

    db = SessionLocal()
    result = evaluate_flag(
        db=db,
        flag_key="dark_mode",
        environment_name="development",
        user_context={
            "user_id": 101,
            "groups": ["admin"],
            "country": "India"
        }
    )
    print(result)
    db.close()
    assert result["success"] is True
    assert result["enabled"] == True  # Replace with the expected default value for the flag

def test_disabled_flag():

    db = SessionLocal()
    result = evaluate_flag(
        db=db,
        flag_key="beta_feature",
        environment_name="production",
        user_context={
            "user_id": 202,
            "groups": ["user"],
            "country": "USA"
        }
    )
    print(result)
    db.close()
    assert result["success"] is True
    assert result["enabled"] is False

def test_envirnment_override():

    db = SessionLocal()
    result = evaluate_flag(
        db=db,
        flag_key="dark_mode",
        environment_name="production",
        user_context={
            "user_id": 303,
            "groups": ["tester"],
            "country": "Canada"
        }
    )
    print(result)
    db.close()
    assert result["success"] is True
    assert result["environment"] == "production"
    assert result["enabled"] is False

def test_empty_user_context():

    db = SessionLocal()
    result = evaluate_flag(
        db=db,
        flag_key="dark_mode",
        environment_name="development",
        user_context={}
    )
    print(result)
    db.close()
    assert result["success"] is True
    assert result["enabled"] is True


if __name__ == "__main__":
    print("--- Running test_default_value_fallback ---")
    test_default_value_fallback()
    print("--- Running test_disabled_flag ---")
    test_disabled_flag()
    print("--- Running test_envirnment_override ---")
    test_envirnment_override()
    print("--- Running test_empty_user_context ---")
    test_empty_user_context()
    print("\nAll test_engine.py tests completed successfully!")