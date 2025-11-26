#tests/core/services/test_validation.py
from app.schemas.lms import LMSDocument
from app.core.services.validation import validate_lms 
def test_validate_lms_valid_document():
    doc = LMSDocument(
        courseId="course_123",
        lessons=[]
    )
    result = validate_lms(doc)
    assert result["valid"] is False
    assert "No lessons found in LMSDocument" in result["errors"]
