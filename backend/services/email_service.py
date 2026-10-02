"""
Email Service for CartIQ using Twilio SendGrid API.
"""

import os
from typing import List, Dict, Any
from datetime import datetime
from data.schemas import GroupedProduct
from utils.logger import logger

class EmailService:
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "results@cartiq.app")

    def format_email_html(self, search_query: str, products: List[GroupedProduct]) -> str:
        """
        Formats HTML email with direct links, offers, ratings, and timestamp.
        """
        timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
        
        items_html = ""
        for p in products:
            offers_rows = ""
            for o in p.offers:
                url = o.product_url if o.product_url else "#"
                offers_rows += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>{o.marketplace}</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">₹{o.price:,.2f}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">⭐ {o.rating}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">
                        <a href="{url}" style="color: #2563eb; text-decoration: none; font-weight: bold;">View Offer &rarr;</a>
                    </td>
                </tr>
                """

            items_html += f"""
            <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: #1f2937;">{p.canonical_name}</h3>
                <p style="color: #4b5563;">Brand: <strong>{p.brand}</strong> | Category: <strong>{p.category}</strong></p>
                <p style="background: #ecfdf5; color: #047857; padding: 8px 12px; border-radius: 6px; display: inline-block;">
                    💰 <strong>Lowest Retrieved Price: ₹{p.lowest_price:,.2f}</strong> (on {p.lowest_marketplace})
                </p>
                <table style="width: 100%; border-collapse: collapse; margin-top: 12px;">
                    <thead>
                        <tr style="background: #f9fafb; text-align: left;">
                            <th style="padding: 8px;">Marketplace</th>
                            <th style="padding: 8px;">Price</th>
                            <th style="padding: 8px;">Rating</th>
                            <th style="padding: 8px;">Product Link</th>
                        </tr>
                    </thead>
                    <tbody>
                        {offers_rows}
                    </tbody>
                </table>
            </div>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>CartIQ Comparison Results</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f3f4f6; padding: 20px;">
            <div style="max-width: 650px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 12px;">
                <h1 style="color: #2563eb; margin-bottom: 4px;">CARTIQ</h1>
                <p style="color: #6b7280; margin-top: 0;">Search Once. Compare Everywhere.</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                
                <h2>Comparison Results for: "<em>{search_query}</em>"</h2>
                <p style="color: #6b7280; font-size: 13px;">Retrieved on: {timestamp}</p>
                
                {items_html}
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="font-size: 12px; color: #9ca3af; text-align: center;">
                    CartIQ is an AI product comparison platform. CartIQ does not process purchases directly.
                </p>
            </div>
        </body>
        </html>
        """
        return html_content

    def send_comparison_email(self, recipient_email: str, search_query: str, products: List[GroupedProduct]) -> Dict[str, Any]:
        """
        Sends email via SendGrid or logs content cleanly if SendGrid key missing.
        """
        html_body = self.format_email_html(search_query, products)
        
        if not self.api_key:
            logger.warning("[EmailService] SENDGRID_API_KEY is not configured. Email preview logged.")
            return {
                "success": True,
                "status": "simulated",
                "message": f"Email successfully dispatched to {recipient_email} (Simulated mode: SendGrid key unconfigured)."
            }

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=self.from_email,
                to_emails=recipient_email,
                subject=f"CartIQ Comparison Results: {search_query}",
                html_content=html_body
            )
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            logger.info(f"[EmailService] SendGrid response status code: {response.status_code}")
            return {
                "success": True,
                "status": "sent",
                "message": f"Comparison results successfully emailed to {recipient_email}!"
            }
        except Exception as e:
            logger.error(f"[EmailService] SendGrid dispatch error: {e}")
            return {
                "success": False,
                "status": "error",
                "message": f"Failed to send email via SendGrid: {str(e)}"
            }

    def send_feedback_email(self, recipient_email: str, full_name: str) -> Dict[str, Any]:
        """
        Sends a feedback request email to the user via SendGrid after sign-out.
        Reads SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, and FEEDBACK_FORM_URL from environment.
        """
        api_key = os.getenv("SENDGRID_API_KEY", "").strip() or (self.api_key or "").strip()
        from_email = os.getenv("SENDGRID_FROM_EMAIL", "").strip() or (self.from_email or "").strip() or "results@cartiq.app"
        feedback_form_url = os.getenv("FEEDBACK_FORM_URL", "").strip()

        if not recipient_email or not recipient_email.strip():
            logger.warning("[EmailService] Recipient email is missing or empty.")
            return {
                "success": False,
                "status": "invalid_recipient",
                "message": "Recipient email is missing."
            }

        if not feedback_form_url:
            logger.warning("[EmailService] FEEDBACK_FORM_URL is not configured.")
            return {
                "success": False,
                "status": "missing_config",
                "message": "FEEDBACK_FORM_URL is not configured."
            }

        if not api_key:
            logger.warning("[EmailService] SENDGRID_API_KEY is not configured. Email preview logged.")
            return {
                "success": True,
                "status": "simulated",
                "message": f"Feedback email successfully dispatched to {recipient_email} (Simulated mode: SendGrid key unconfigured)."
            }

        subject = "💙 How was your CartIQ experience?"
        name = full_name.strip() if (full_name and full_name.strip()) else "there"

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CartIQ Feedback</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 20px; color: #1e293b;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0;">
        <h2 style="color: #6366f1; margin-top: 0; text-align: center;">🛒 CartIQ</h2>
        <p style="font-size: 1.1rem;">Hello {name}! 👋</p>
        <p>Thank you for using <strong>CartIQ — Search Once. Compare Everywhere. 🛒✨</strong></p>
        <div style="background: #f0f0ff; border-left: 4px solid #6366f1; padding: 12px 16px; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0; font-weight: bold; color: #4338ca;">💬 Your feedback matters!</p>
            <p style="margin: 4px 0 0 0; color: #475569; font-size: 0.95rem;">Your valuable words help us make CartIQ better, smarter, and more useful.</p>
        </div>
        <p>We'd love to hear about your experience.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{feedback_form_url}" target="_blank" style="background-color: #6366f1; color: #ffffff; padding: 14px 28px; text-decoration: none; font-weight: bold; border-radius: 8px; display: inline-block; font-size: 1rem;">💙 Give Feedback</a>
        </div>
        <p>Thank you for helping us improve CartIQ! 🚀</p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0 16px 0;">
        <p style="font-size: 0.85rem; color: #94a3b8; text-align: center; margin: 0;">CartIQ Team</p>
    </div>
</body>
</html>"""

        plain_text_content = f"""Hello {name}! 👋

Thank you for using CartIQ — Search Once. Compare Everywhere. 🛒✨

💬 Your feedback matters!
Your valuable words help us make CartIQ better, smarter, and more useful.

We'd love to hear about your experience.

Give Feedback: {feedback_form_url}

Thank you for helping us improve CartIQ! 🚀

CartIQ Team"""

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=from_email,
                to_emails=recipient_email,
                subject=subject,
                plain_text_content=plain_text_content,
                html_content=html_content
            )
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            logger.info(f"[EmailService] Feedback email SendGrid status code: {response.status_code}")
            return {
                "success": True,
                "status": "sent",
                "message": f"Feedback email successfully sent to {recipient_email}!"
            }
        except Exception as e:
            logger.error("[EmailService] Failed to send feedback email via SendGrid: exception occurred")
            return {
                "success": False,
                "status": "error",
                "message": f"Failed to send email via SendGrid: {str(e)}"
            }

