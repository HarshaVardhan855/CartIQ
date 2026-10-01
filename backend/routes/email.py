"""
FastAPI Route for /api/email-results.
"""

from fastapi import APIRouter, HTTPException
from data.schemas import EmailRequest
from backend.services.email_service import EmailService

router = APIRouter(prefix="/api", tags=["Email"])
email_service = EmailService()

@router.post("/email-results")
def email_comparison_results(payload: EmailRequest):
    """
    POST /api/email-results
    Sends comparison results to specified email address via SendGrid.
    """
    try:
        res = email_service.send_comparison_email(
            recipient_email=payload.recipient_email,
            search_query=payload.search_query,
            products=payload.products
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
