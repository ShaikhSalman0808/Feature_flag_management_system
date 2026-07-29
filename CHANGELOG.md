# Feature Flag Management System - Change Log

All notable changes and updates to this project are documented in this file.

---

## [2026-07-29] - User Context Evaluation & Production Flag Seeding

### Added
- **`user_context` Support in Evaluation Engine** (`app/services/evaluation_engine.py`):
  - Added optional `user_context` parameter to `evaluate_flag()`, `evaluate_targeting_rules()`, and `evaluate_rule_condition()`.
  - Added support for targeting rule operator matching (`EQUALS`, `NOT_EQUALS`, `CONTAINS`, `IN`, `GREATER_THAN`, `LESS_THAN`).
- **Production Flags Seeding** (`app/database/seed.py`):
  - Added production environment seed records (`new_checkout_flow`, `dark_mode_theme`, `ai_recommendations`, `payment_gateway_v3`, `beta_search_engine`, `analytics_v2`).
  - Added targeting rules seeding for beta user testing in production.
- **Unit Tests** (`tests/test_engine.py`):
  - Added 9 unit tests covering `user_context` matching, fallback behaviors, globally disabled overrides, and safe numeric condition handling.

### Fixed
- **Database Connection Config** (`app/database/config.py`):
  - Updated `DATABASE_URL` setup using `os.getenv("DATABASE_URL", "postgresql://postgres:sql@localhost:5432/feature_flag_db")` to correctly parse environment variable key and default fallback.
- **Flag Model** (`app/models/flag.py`):
  - Added `name` column to `Flag` model schema.
- **Git Ignore** (`.gitignore`):
  - Added `*.db` and `*.sqlite3` to ignore local SQLite test database files.
