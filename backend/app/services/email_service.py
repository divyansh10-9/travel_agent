# backend/app/services/email_service.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def send_itinerary_email_service(request):
    try:
        # Create email content
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #0066cc;">✈️ Your Travel Itinerary to {request.itinerary.get('destination', 'your destination')}</h1>
                    
                    {f'<p style="font-size: 16px;">{request.itinerary.get("summary", "")}</p>' if request.itinerary.get("summary") else ''}
                    
                    {f'<p style="background: #f0f8ff; padding: 10px; border-radius: 5px;"><strong>Personal Note:</strong> {request.personal_message}</p>' if request.personal_message else ''}
                    
                    <h2 style="color: #0066cc; border-bottom: 2px solid #0066cc; padding-bottom: 5px;">📅 Daily Plans</h2>
                    
                    {''.join([
                        f"""
                        <div style="margin-bottom: 25px; border: 1px solid #ddd; border-radius: 5px; padding: 15px; background: #f9f9f9;">
                            <h3 style="color: #0066cc;">Day {day['day']}: {day.get('date', '')}</h3>
                            {f'<p><strong>✈️ Flight Arrival:</strong> {day.get("arrival_info", "")}</p>' if day.get("arrival_info") else ''}
                            
                            {''.join([
                                f"""
                                <div style="margin: 15px 0;">
                                    <h4 style="color: #0066cc; margin-bottom: 5px;">{slot_name.title()} ({slot['time']})</h4>
                                    <ul style="margin-top: 5px; padding-left: 20px;">
                                        {''.join([f'<li style="margin-bottom: 5px;">{activity}</li>' for activity in slot.get("activities", [])])}
                                    </ul>
                                </div>
                                """ for slot_name, slot in day.get('time_slots', {}).items()
                            ])}
                            
                            {f'<p style="margin-top: 10px;"><strong>🌟 Highlights:</strong> {", ".join(day.get("highlights", []))}</p>' if day.get("highlights") else ''}
                        </div>
                        """ for day in request.itinerary.get('daily_plans', [])
                    ])}
                    
                    <div style="display: flex; margin-top: 30px;">
                        <div style="flex: 1; padding: 10px; background: #f0f8ff; border-radius: 5px; margin-right: 10px;">
                            <h3 style="color: #0066cc;">🧳 Packing List</h3>
                            <ul style="padding-left: 20px;">
                                {''.join([f'<li style="margin-bottom: 5px;">{item}</li>' for item in request.itinerary.get('packing_list', [])])}
                            </ul>
                        </div>
                        
                        <div style="flex: 1; padding: 10px; background: #f0f8ff; border-radius: 5px;">
                            <h3 style="color: #0066cc;">💡 Local Tips</h3>
                            <ul style="padding-left: 20px;">
                                {''.join([f'<li style="margin-bottom: 5px;">{tip}</li>' for tip in request.itinerary.get('local_tips', [])])}
                            </ul>
                        </div>
                    </div>
                    
                    <p style="margin-top: 30px; text-align: center; font-style: italic;">
                        Happy travels! ✈️🌍<br>
                        <span style="color: #0066cc;">Travel Planner Pro</span>
                    </p>
                </div>
            </body>
        </html>
        """

        # Create SendGrid email
        message = Mail(
            from_email=From(os.getenv("SENDGRID_FROM_EMAIL"), os.getenv("SENDGRID_FROM_NAME")),
            to_emails=To(request.email),
            subject=Subject(f"Your Travel Itinerary to {request.itinerary.get('destination', 'your destination')}"),
            html_content=HtmlContent(html_content))
        
        # Send email
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        
        if response.status_code == 202:
            return {"status": "success", "message": "Itinerary sent successfully"}
        else:
            raise Exception(f"SendGrid error: {response.status_code} - {response.body}")

    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        raise HTTPException(500, f"Failed to send email: {str(e)}")