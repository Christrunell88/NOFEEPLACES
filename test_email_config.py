#!/usr/bin/env python3
"""
Test Email Configuration for NoFeePlaces.com
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

def test_email_connection():
    """Test the email configuration"""
    load_dotenv('/app/backend/.env')
    
    smtp_server = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('EMAIL_PORT', '587'))
    email_user = os.environ.get('EMAIL_USER', 'placesfirm@gmail.com') 
    email_password = os.environ.get('EMAIL_PASSWORD', '')
    
    print(f"Testing email configuration:")
    print(f"SMTP Server: {smtp_server}:{smtp_port}")
    print(f"Email User: {email_user}")
    print(f"Password configured: {'Yes' if email_password else 'No'}")
    
    if not email_password:
        print("❌ ERROR: No email password configured")
        return False
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['Subject'] = "NoFeePlaces.com Email Service Test"
        msg['From'] = f"NoFeePlaces.com <{email_user}>"
        msg['To'] = email_user  # Send to self for testing
        
        # Add body
        body = """
        This is a test email from NoFeePlaces.com email service.
        
        If you receive this email, the email configuration is working correctly.
        
        Best regards,
        NoFeePlaces.com Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        print("Starting TLS...")
        server.starttls(context=ssl.create_default_context())
        
        print("Attempting login...")
        server.login(email_user, email_password)
        
        print("Sending test email...")
        server.send_message(msg)
        server.quit()
        
        print("✅ SUCCESS: Test email sent successfully!")
        print(f"Check the inbox at {email_user}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Email test failed: {str(e)}")
        
        # Provide specific guidance based on error type
        error_str = str(e).lower()
        if 'username and password not accepted' in error_str:
            print("\n💡 TROUBLESHOOTING TIPS:")
            print("1. Enable 2-Factor Authentication on your Gmail account")
            print("2. Generate an App Password specifically for this application")
            print("3. Use the App Password instead of your regular Gmail password")
            print("4. Go to: Google Account > Security > 2-Step Verification > App passwords")
            print("5. Generate password for 'Mail' and use that in EMAIL_PASSWORD")
        
        return False

if __name__ == "__main__":
    print("🧪 Testing NoFeePlaces.com Email Configuration")
    print("=" * 50)
    test_email_connection()