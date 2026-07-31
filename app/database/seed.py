import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.database.session import SessionLocal
from app.models.environment import Environment
from app.models.flag import Flag


def get_or_create_env(db, name, description):
    env = db.query(Environment).filter(Environment.name == name).first()
    if not env:
        env = Environment(name=name, description=description)
        db.add(env)
        db.commit()
        db.refresh(env)
    return env


def get_or_create_flag(db, name, key, flag_type, description, enabled, env_id, default_value, owner_team):
    flag = db.query(Flag).filter(Flag.key == key, Flag.environment_id == env_id).first()
    if not flag:
        flag = Flag(
            name=name,
            key=key,
            type=flag_type,
            description=description,
            enabled=enabled,
            environment_id=env_id,
            default_value=default_value,
            owner_team=owner_team,
        )
        db.add(flag)
        db.commit()
        db.refresh(flag)
    return flag


def seed_data():
    db = SessionLocal()
    try:
        dev_env = get_or_create_env(db, "development", "Development Environment")
        staging_env = get_or_create_env(db, "staging", "Staging Environment")
        prod_env = get_or_create_env(db, "production", "Production Environment")

        get_or_create_flag(
            db, "Dark Mode Theme", "dark_mode", "boolean", "Enables dark mode UI theme", True, dev_env.id, "true", "FrontendTeam"
        )
        get_or_create_flag(
            db, "New Checkout Flow", "new_checkout", "boolean", "Enables v2 checkout UI", True, dev_env.id, "v2", "CheckoutTeam"
        )
        get_or_create_flag(
            db, "Dark Mode Theme", "dark_mode", "boolean", "Enables dark mode UI theme", False, prod_env.id, "false", "FrontendTeam"
        )
        get_or_create_flag(
            db, "Beta Feature", "beta_feature", "boolean", "Enables beta feature", False, prod_env.id, "false", "CoreTeam"
        )

        print("Database seeded successfully with environments and feature flags.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
