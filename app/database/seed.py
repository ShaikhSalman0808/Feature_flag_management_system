import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.database.session import SessionLocal
from app.models.environment import Environment
from app.models.flag import Flag


def seed_data():
    db = SessionLocal()
    try:
        # Create Environments
        dev_env = Environment(name="development", description="Development Environment")
        staging_env = Environment(name="staging", description="Staging Environment")
        prod_env = Environment(name="production", description="Production Environment")

        db.add_all([dev_env, staging_env, prod_env])
        db.commit()

        db.refresh(dev_env)
        db.refresh(staging_env)
        db.refresh(prod_env)

        # Create Feature Flags
        dark_mode_dev = Flag(
            name="Dark Mode Theme",
            key="dark_mode",
            type="boolean",
            description="Enables dark mode UI theme",
            enabled=True,
            environment_id=dev_env.id,
            default_value="true",
            owner_team="FrontendTeam",
        )
        checkout_dev = Flag(
            name="New Checkout Flow",
            key="new_checkout",
            type="boolean",
            description="Enables v2 checkout UI",
            enabled=True,
            environment_id=dev_env.id,
            default_value="v2",
            owner_team="CheckoutTeam",
        )

        dark_mode_prod = Flag(
            name="Dark Mode Theme",
            key="dark_mode",
            type="boolean",
            description="Enables dark mode UI theme",
            enabled=False,
            environment_id=prod_env.id,
            default_value="false",
            owner_team="FrontendTeam",
        )

        db.add_all([dark_mode_dev, checkout_dev, dark_mode_prod])
        db.commit()
        print("Original database seeded successfully with environments and feature flags.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
