from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.models.environment import Environment
from app.models.flag import Flag
from app.models.targeting_rule import TargetingRule


def evaluate_rule_condition(
    attribute_val: Any,
    operator: str,
    target_val: str,
    user_context: Optional[Dict[str, Any]] = None,
) -> bool:
    """Evaluates a single attribute rule against target value with operator."""
    if attribute_val is None:
        return False

    op = operator.upper() if operator else "EQUALS"
    attr_str = str(attribute_val).strip().lower()
    target_str = str(target_val).strip().lower()

    if op in ("EQUALS", "==", "EQ"):
        return attr_str == target_str
    elif op in ("NOT_EQUALS", "!=", "NEQ"):
        return attr_str != target_str
    elif op in ("CONTAINS", "HAS"):
        return target_str in attr_str
    elif op in ("IN", "MEMBER_OF"):
        target_list = [v.strip().lower() for v in target_val.split(",")]
        return attr_str in target_list
    elif op in ("GREATER_THAN", ">", "GT"):
        try:
            return float(attribute_val) > float(target_val)
        except (ValueError, TypeError):
            return False
    elif op in ("LESS_THAN", "<", "LT"):
        try:
            return float(attribute_val) < float(target_val)
        except (ValueError, TypeError):
            return False

    return attr_str == target_str


def evaluate_targeting_rules(
    db: Session,
    flag_id: int,
    user_context: Optional[Dict[str, Any]] = None,
) -> Optional[bool]:
    """Evaluates targeting rules for a flag using user_context.

    Returns True if user_context satisfies a targeting rule,
    False if targeting rules exist but none match,
    or None if no targeting rules are defined.
    """
    if not user_context:
        return None

    rules = db.query(TargetingRule).filter(TargetingRule.flag_id == flag_id).all()
    if not rules:
        return None

    for rule in rules:
        attr_name = rule.attribute
        if not attr_name:
            continue

        user_val = user_context.get(attr_name)
        if evaluate_rule_condition(user_val, rule.operator, rule.value, user_context=user_context):
            return True

    return False


def evaluate_flag(
    db: Session,
    flag_key: str,
    environment_name: str,
    user_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Evaluates feature flag status and value for a given environment and optional user_context."""
    environment = (
        db.query(Environment)
        .filter(Environment.name == environment_name)
        .first()
    )

    if environment is None:
        return {
            "success": False,
            "message": "Environment not found",
        }

    flag = (
        db.query(Flag)
        .filter(
            Flag.key == flag_key,
            Flag.environment_id == environment.id,
        )
        .first()
    )

    if flag is None:
        return {
            "success": False,
            "message": "Feature flag not found",
        }

    if not flag.enabled:
        return {
            "success": True,
            "flag": flag.key,
            "enabled": False,
            "value": flag.default_value,
            "user_context": user_context,
        }

    rule_result = evaluate_targeting_rules(db, flag.id, user_context=user_context)
    if rule_result is not None:
        return {
            "success": True,
            "flag": flag.key,
            "enabled": rule_result,
            "value": flag.default_value,
            "user_context": user_context,
        }

    return {
        "success": True,
        "flag": flag.key,
        "enabled": flag.enabled,
        "value": flag.default_value,
        "user_context": user_context,
    }
