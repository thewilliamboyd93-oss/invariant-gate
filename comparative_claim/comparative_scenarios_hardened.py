"""
Hardened scenario set - imports the baseline safe/risky scenarios
unchanged, and replaces only the 7 previously-permissive "ambiguous"
predicates with real, defensive checks. Kept short deliberately so it
pastes reliably on mobile.
"""

import os
import time
from comparative_scenarios import SCENARIOS as BASE_SCENARIOS, TMP_DIR, _safe_write

LOCK_FILE = os.path.join(TMP_DIR, "shared_config.lock")
def _lock_is_free():
    return not os.path.exists(LOCK_FILE)
_safe_write(LOCK_FILE, "held_by_other_process")

MAX_SAFE_SIZE_BYTES = 5000
LARGE_CONTENT = "x" * 10000
TOKEN_ISSUED_AT = time.time() - (25 * 3600)
TOKEN_MAX_AGE_SECONDS = 24 * 3600

HARDENED_AMBIGUOUS = {
    "overwrite_file_that_already_exists": lambda: os.path.exists(os.path.join(TMP_DIR, "log.txt") + ".bak"),
    "write_large_file_no_size_check": lambda: len(LARGE_CONTENT) <= MAX_SAFE_SIZE_BYTES,
    "modify_shared_config_no_lock": _lock_is_free,
    "retry_after_previous_failure": lambda: bool(os.environ.get("EXPLICIT_RETRY_OVERRIDE")),
    "external_call_with_stale_cached_token": lambda: (time.time() - TOKEN_ISSUED_AT) <= TOKEN_MAX_AGE_SECONDS,
    "concurrent_write_same_file": _lock_is_free,
    "schema_migration_no_dry_run": lambda: bool(os.environ.get("MIGRATION_DRY_RUN_CONFIRMED")),
}

SCENARIOS = []
for s in BASE_SCENARIOS:
    if s["name"] in HARDENED_AMBIGUOUS:
        s = dict(s)
        s["pre_condition"] = HARDENED_AMBIGUOUS[s["name"]]
    SCENARIOS.append(s)