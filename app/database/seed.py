import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.database.base import Base
from app.database.session import SessionLocal, engine
import app.models  # Ensure all models are registered with Base
from app.models.environment import Environment
from app.models.flag import Flag
from app.models.targeting_rule import TargetingRule


def seed_data():
    Base.metadata.create_all(bind=engine)
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
            # Production Flags
            {
                "name": "New Checkout Flow",
                "key": "new_checkout_flow",
                "type": "boolean",
                "description": "Enables the new multi-step checkout UI in Production",
                "enabled": True,
                "environment_id": environments_map["Production"],
                "default_value": "v2",
                "owner_team": "CheckoutTeam",
            },
            {
                "name": "Dark Mode Theme",
                "key": "dark_mode_theme",
                "type": "string",
                "description": "Enables dark mode theme toggle for Production users",
                "enabled": True,
                "environment_id": environments_map["Production"],
                "default_value": "dark",
                "owner_team": "FrontendTeam",
            },
            {
                "name": "AI Recommendations",
                "key": "ai_recommendations",
                "type": "boolean",
                "description": "AI-powered product recommendations widget in Production",
                "enabled": False,
                "environment_id": environments_map["Production"],
                "default_value": "disabled",
                "owner_team": "MLTeam",
            },
            {
                "name": "Payment Gateway V3",
                "key": "payment_gateway_v3",
                "type": "string",
                "description": "Upgraded Stripe & PayPal checkout API in Production",
                "enabled": True,
                "environment_id": environments_map["Production"],
                "default_value": "stripe_v3",
                "owner_team": "PaymentsTeam",
            },
            {
                "name": "Beta Search Engine",
                "key": "beta_search_engine",
                "type": "string",
                "description": "Vector search backend for targeted users in Production",
                "enabled": True,
                "environment_id": environments_map["Production"],
                "default_value": "vector_v1",
                "owner_team": "SearchTeam",
            },
            {
                "name": "Analytics V2",
                "key": "analytics_v2",
                "type": "boolean",
                "description": "Real-time user analytics tracking in Production",
                "enabled": True,
                "environment_id": environments_map["Production"],
                "default_value": "enabled",
                "owner_team": "DataTeam",
            },

            # Non-Production Flags
            {
                "name": "Dark Mode Theme (Dev)",
                "key": "dark_mode_theme",
                "type": "string",
                "description": "Enables dark mode theme toggle for Dev testing",
                "enabled": True,
                "environment_id": environments_map["Development"],
                "default_value": "dark",
                "owner_team": "FrontendTeam",
            },
            {
                "name": "AI Recommendations (Staging)",
                "key": "ai_recommendations",
                "type": "boolean",
                "description": "AI product recommendations widget in Staging",
                "enabled": False,
                "environment_id": environments_map["Staging"],
                "default_value": "off",
                "owner_team": "MLTeam",
            },
            {
                "name": "Beta Search Engine (QA)",
                "key": "beta_search_engine",
                "type": "string",
                "description": "Vector search backend in QA environment",
                "enabled": True,
                "environment_id": environments_map["QA"],
                "default_value": "vector_v1",
                "owner_team": "SearchTeam",
            },
            {
                "name": "Payment Gateway V3 (Sandbox)",
                "key": "payment_gateway_v3",
                "type": "string",
                "description": "Upgraded checkout API in Sandbox environment",
                "enabled": False,
                "environment_id": environments_map["Sandbox"],
                "default_value": "v2",
                "owner_team": "PaymentsTeam",
            },
        ]

        flag_id_map = {}
        for flag_info in flags_data:
            existing_flag = db.query(Flag).filter(
                Flag.key == flag_info["key"],
                Flag.environment_id == flag_info["environment_id"]
            ).first()
            if not existing_flag:
                flag = Flag(**flag_info)
                db.add(flag)
                db.flush()
                flag_id_map[(flag.key, flag.environment_id)] = flag.id
                print(f"  [+] Added Flag: {flag.key} (Env ID: {flag.environment_id})")
            else:
                flag_id_map[(existing_flag.key, existing_flag.environment_id)] = existing_flag.id
                print(f"  [=] Flag '{existing_flag.key}' (Env ID: {existing_flag.environment_id}) already exists.")

        print("\n--- Seeding targeting rules ---")
        beta_search_prod_id = flag_id_map.get(("beta_search_engine", environments_map["Production"]))
        if beta_search_prod_id:
            existing_rule = db.query(TargetingRule).filter(
                TargetingRule.flag_id == beta_search_prod_id,
                TargetingRule.attribute == "group"
            ).first()
            if not existing_rule:
                rule = TargetingRule(
                    flag_id=beta_search_prod_id,
                    attribute="group",
                    operator="EQUALS",
                    value="beta_testers"
                )
                db.add(rule)
                print(f"  [+] Added TargetingRule for flag ID {beta_search_prod_id}")
            else:
                print(f"  [=] TargetingRule for flag ID {beta_search_prod_id} already exists.")

        db.commit()
        print("\n[SUCCESS] Database seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
