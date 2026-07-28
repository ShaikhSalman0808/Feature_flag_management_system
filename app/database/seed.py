import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.database.session import SessionLocal
from app.models.environment import Environment
from app.models.flag import Flag


def seed_data():
    db = SessionLocal()
    try:
        print("--- Seeding environments ---")
        environments_data = [
            {"name": "Development", "description": "Development environment for internal testing"},
            {"name": "Staging", "description": "Staging environment for pre-release validation"},
            {"name": "Production", "description": "Production environment serving live users"},
            {"name": "QA", "description": "Quality assurance environment for automated testing"},
            {"name": "Sandbox", "description": "Isolated sandbox environment for experimental features"},
        ]

        environments_map = {}
        for env_info in environments_data:
            existing_env = db.query(Environment).filter(Environment.name == env_info["name"]).first()
            if not existing_env:
                env = Environment(**env_info)
                db.add(env)
                db.flush()
                environments_map[env.name] = env.id
                print(f"  [+] Added Environment: {env.name}")
            else:
                environments_map[existing_env.name] = existing_env.id
                print(f"  [=] Environment '{existing_env.name}' already exists.")

        print("\n--- Seeding feature flags ---")
        flags_data = [
            {
                "name": "New Checkout Flow",
                "key": "new_checkout_flow",
                "description": "Enables the new multi-step checkout UI",
                "is_enabled": True,
                "environment_id": environments_map["Production"],
                "default_value": "v2",
            },
            {
                "name": "Dark Mode Theme",
                "key": "dark_mode_theme",
                "description": "Enables dark mode theme toggle for users",
                "is_enabled": True,
                "environment_id": environments_map["Development"],
                "default_value": "dark",
            },
            {
                "name": "AI Recommendations",
                "key": "ai_recommendations",
                "description": "Enables AI-powered product recommendations widget",
                "is_enabled": False,
                "environment_id": environments_map["Staging"],
                "default_value": "off",
            },
            {
                "name": "Beta Search Engine",
                "key": "beta_search_engine",
                "description": "Enables new vector search backend",
                "is_enabled": True,
                "environment_id": environments_map["QA"],
                "default_value": "vector_v1",
            },
            {
                "name": "Payment Gateway V3",
                "key": "payment_gateway_v3",
                "description": "Enables upgraded Stripe & PayPal checkout API",
                "is_enabled": False,
                "environment_id": environments_map["Sandbox"],
                "default_value": "v2",
            },
        ]

        for flag_info in flags_data:
            existing_flag = db.query(Flag).filter(Flag.key == flag_info["key"]).first()
            if not existing_flag:
                flag = Flag(**flag_info)
                db.add(flag)
                print(f"  [+] Added Flag: {flag.key} ({flag.name})")
            else:
                print(f"  [=] Flag '{existing_flag.key}' already exists.")

        db.commit()
        print("\n[SUCCESS] Database seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
