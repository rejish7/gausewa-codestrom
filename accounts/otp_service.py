import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class OTPService:
    """Service to handle OTP sending via SMS"""
    
    @staticmethod
    def send_otp(phone_number, otp_code):
        
        # For development: Just log the OTP
        if settings.DEBUG:
            logger.info(f"OTP for {phone_number}: {otp_code}")
            print(f"\n{'='*50}")
            print(f"OTP SENT TO: {phone_number}")
            print(f"OTP CODE: {otp_code}")
            print(f"{'='*50}\n")
            return True
        
        # Production: Integrate with actual SMS gateway
        try:
            # Example for Sparrow SMS (Nepal)
            # sms_url = "https://sms.aakashsms.com/sms/v3/send"
            # payload = {
            #     'auth_token': settings.SMS_AUTH_TOKEN,
            #     'to': phone_number,
            #     'text': f'Your Gausewa OTP is: {otp_code}. Valid for 5 minutes.'
            # }
            # response = requests.post(sms_url, data=payload)
            # return response.status_code == 200
            
            # Example for Twilio
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=f'Your Gausewa OTP is: {otp_code}. Valid for 5 minutes.',
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=phone_number
            # )
            # return message.sid is not None
            
            logger.warning("SMS gateway not configured for production")
            return False
            
        except Exception as e:
            logger.error(f"Error sending OTP: {str(e)}")
            return False
