from sqlalchemy.orm import Session
from app.models.environment import Environment
from app.models.flag import Flag
from app.models.targeting_rule import TargetingRule
from app.models.user_group_membership import UserGroupMembership


def evaluate_flag(
    db: Session,
    flag_key: str,
    environment_name: str,
    user_context: dict | None = None
):
    environment = (
        db.query(Environment)
        .filter(Environment.name == environment_name)
        .first()
    )
    if environment is None:
        return {
            "success": False,
            "message": "Environment not found"
        }
    flag = (
        db.query(Flag)
        .filter(
            Flag.key == flag_key,
            Flag.environment_id == environment.id
        )
        .first()
    )
    if flag is None:
        return {
            "success": False,
            "message": "Feature flag not found"
        }

    if user_context:
        user_id = str(user_context.get("user_id"))

        rule = (
            db.query(TargetingRule).filter(
                TargetingRule.flag_id == flag.id,
                TargetingRule.attribute == "user_id",
                TargetingRule.operator == "=",
                TargetingRule.value == user_id
            ).first()
        )

        if rule:
            return {
                "success": True,
                "message": "Matched User Targeting Rule",
                "environment": environment.name,
                "flag": flag.key,
                "type": flag.type,
                "enabled": flag.enabled,
                "value": flag.default_value,
                "user_context": user_context
            }

        group_membership = (
            db.query(UserGroupMembership)
            .filter(UserGroupMembership.user_id == user_id)
            .first()
        )

        if group_membership:
            group_rule = (
                db.query(TargetingRule)
                .filter(
                    TargetingRule.flag_id == flag.id,
                    TargetingRule.attribute.in_(["group_name", "group_id"]),
                    TargetingRule.operator == "=",
                    TargetingRule.value == group_membership.group_name
                )
                .first()
            )

            if group_rule:
                return {
                    "success": True,
                    "message": "Matched Group Targeting Rule",
                    "environment": environment.name,
                    "flag": flag.key,
                    "type": flag.type,
                    "enabled": flag.enabled,
                    "value": flag.default_value,
                    "user_context": user_context
                }

    return {
        "success": True,
        "environment": environment.name,
        "flag": flag.key,
        "type": flag.type,
        "enabled": flag.enabled,
        "value": flag.default_value,
        "user_context": user_context
    }

