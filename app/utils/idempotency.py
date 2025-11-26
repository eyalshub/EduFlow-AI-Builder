# app/utils/idempotency.py
import uuid
from datetime import datetime

def new_pipeline_run_id(prefix: str = "run") -> str:
    """
    Generates a unique pipeline run ID using timestamp and UUID.
    Format: run_YYYYMMDD_HHMMSS_UUID4
    """
    now_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:8]
    return f"{prefix}_{now_str}_{uid}"
