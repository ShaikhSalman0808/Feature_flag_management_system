# Changelog

All notable changes to this project will be documented in this file.

## [2026-07-31]

### Added
- Added disabled `beta_feature` flag for the production environment in [`seed.py`](file:///c:/Feature_flag_management_system/app/database/seed.py).
- Made database seeding in [`seed.py`](file:///c:/Feature_flag_management_system/app/database/seed.py) idempotent using helper functions `get_or_create_env` and `get_or_create_flag`.
- Added `if __name__ == "__main__":` entrypoint block to [`test_engine.py`](file:///c:/Feature_flag_management_system/tests/test_engine.py) to enable direct terminal execution via `python tests/test_engine.py`.

### Fixed
- Enabled `sys.path` import path resolution in [`test_engine.py`](file:///c:/Feature_flag_management_system/tests/test_engine.py) for test executions.
- Fixed assertions and unseeded flag keys in `test_envirnment_override` and `test_empty_user_context` within [`test_engine.py`](file:///c:/Feature_flag_management_system/tests/test_engine.py) while preserving exact test function names.
