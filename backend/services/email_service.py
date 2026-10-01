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
