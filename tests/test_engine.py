import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import SessionLocal
from app.models.environment import Environment
from app.models.flag import Flag
from app.models.targeting_rule import TargetingRule
from app.models.user_group_membership import UserGroupMembership
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
    assert result["enabled"] == True  
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


def test_user_targeting():

    db = SessionLocal()
    try:
        env = db.query(Environment).filter(Environment.name == "development").first()
        flag = db.query(Flag).filter(Flag.key == "dark_mode", Flag.environment_id == env.id).first()

        rule = db.query(TargetingRule).filter(TargetingRule.flag_id == flag.id, TargetingRule.attribute == "user_id").first()
        if not rule:
            rule = TargetingRule(flag_id=flag.id, attribute="user_id", operator="=", value="101")
            db.add(rule)
            db.commit()
            db.refresh(rule)
        else:
            rule.operator = "="
            rule.value = "101"
            db.commit()

        result = evaluate_flag(
            db=db,
            flag_key="dark_mode",
            environment_name="development",
            user_context={
                "user_id": "101"
            }
        )
        print("Targeting match result:", result)
        assert result["success"] is True
        assert result["message"] == "Matched User Targeting Rule"
    finally:
        db.close()

def test_user_group_targeting():

    db = SessionLocal()
    try:
        env = db.query(Environment).filter(Environment.name == "development").first()
        flag = db.query(Flag).filter(Flag.key == "dark_mode", Flag.environment_id == env.id).first()

        membership = db.query(UserGroupMembership).filter(UserGroupMembership.user_id == "102").first()
        if not membership:
            membership = UserGroupMembership(user_id="102", group_name="admin")
            db.add(membership)
            db.commit()
            db.refresh(membership)
        else:
            membership.group_name = "admin"
            db.commit()

        rule = db.query(TargetingRule).filter(TargetingRule.flag_id == flag.id, TargetingRule.attribute == "group_name").first()
        if not rule:
            rule = TargetingRule(flag_id=flag.id, attribute="group_name", operator="=", value="admin")
            db.add(rule)
            db.commit()
            db.refresh(rule)
        else:
            rule.attribute = "group_name"
            rule.operator = "="
            rule.value = "admin"
            db.commit()

        result = evaluate_flag(
            db=db,
            flag_key="dark_mode",
            environment_name="development",
            user_context={
                "user_id": "102",
                "groups": ["admin", "team1"],
                "country": "US"
            }
        )
        print("Group targeting match result:", result)
        assert result["success"] is True
        assert result["message"] == "Matched Group Targeting Rule"
    finally:
        db.close()


if __name__ == "__main__":
    print("--- Running test_default_value_fallback ---")
    test_default_value_fallback()
    print("--- Running test_disabled_flag ---")
    test_disabled_flag()
    print("--- Running test_envirnment_override ---")
    test_envirnment_override()
    print("--- Running test_empty_user_context ---")
    test_empty_user_context()
    print("--- Running test_user_targeting ---")
    test_user_targeting()
    print("--- Running test_user_group_targeting ---")
    test_user_group_targeting()
    print("\nAll test_engine.py tests completed successfully!")