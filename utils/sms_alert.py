"""
Emergency SMS Alert System
For demo purposes, this prints to console.
To enable actual SMS, configure Twilio API keys.
"""

import os
from datetime import datetime

class SMSAlert:
    """Emergency SMS Alert System for Hyphema Detection"""
    
    def __init__(self):
        # For demo mode (prints to console)
        self.demo_mode = True
        
        # Twilio configuration (optional - uncomment to enable)
        # self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
        # self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
        # self.from_number = os.environ.get('TWILIO_FROM_NUMBER', '')
        # self.demo_mode = not (self.account_sid and self.auth_token and self.from_number)
    
    def send_emergency_alert(self, phone_number, patient_name, severity, severity_grade, hospital_name=None, hospital_phone=None):
        """
        Send emergency SMS alert for severe hyphema cases (Grade 3 or 4)
        """
        if not phone_number:
            print("⚠️ No phone number provided - skipping SMS")
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
🚨 EMERGENCY MEDICAL ALERT 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━
Patient: {patient_name}
Time: {timestamp}
Condition: HYPHEMA DETECTED
Severity: Grade {severity_grade} - {severity}

⚠️ IMMEDIATE ACTION REQUIRED:
• Seek emergency eye care immediately
• Do NOT drive yourself
• Keep head elevated (30-45 degrees)
• Do NOT rub or press the eye
• Use eye shield if available

{f'🏥 Nearest Hospital: {hospital_name}' if hospital_name else ''}
{f'📞 Hospital Phone: {hospital_phone}' if hospital_phone else ''}

This is an automated alert from Hyphema Detection System.
Please consult an ophthalmologist immediately.
━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
        
        if self.demo_mode:
            # Demo mode - print to console
            print("\n" + "=" * 60)
            print("📱 EMERGENCY SMS ALERT (DEMO MODE)")
            print("=" * 60)
            print(f"To: {phone_number}")
            print(message)
            print("=" * 60 + "\n")
            return True
        else:
            # Production mode - send via Twilio
            try:
                from twilio.rest import Client
                client = Client(self.account_sid, self.auth_token)
                client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=phone_number
                )
                print(f"✅ Emergency SMS sent to {phone_number}")
                return True
            except Exception as e:
                print(f"❌ SMS failed: {e}")
                return False
    
    def send_appointment_reminder(self, phone_number, patient_name, hospital_name, appointment_date, appointment_time):
        """
        Send appointment reminder SMS
        """
        if not phone_number:
            return False
        
        message = f"""
📅 APPOINTMENT REMINDER
━━━━━━━━━━━━━━━━━━
Patient: {patient_name}
Hospital: {hospital_name}
Date: {appointment_date}
Time: {appointment_time}

Please bring:
• ID proof
• Previous medical records
• Insurance card (if any)

Reply CONFIRM to confirm attendance.
━━━━━━━━━━━━━━━━━━
        """.strip()
        
        if self.demo_mode:
            print("\n" + "=" * 50)
            print("📱 APPOINTMENT REMINDER (DEMO MODE)")
            print("=" * 50)
            print(f"To: {phone_number}")
            print(message)
            print("=" * 50 + "\n")
            return True
        
        return False
    
    def send_followup_reminder(self, phone_number, patient_name, days=7):
        """
        Send follow-up reminder after hyphema detection
        """
        message = f"""
👁 FOLLOW-UP REMINDER

Dear {patient_name},

It's been {days} days since your hyphema detection.
Please schedule a follow-up appointment with your ophthalmologist.

Your eye health is important. Early follow-up prevents complications.

Reply STATUS to update your condition.
        """.strip()
        
        if self.demo_mode:
            print(f"📱 Follow-up reminder sent to {phone_number}")
            return True
        
        return False

# Create global instance
sms_alert = SMSAlert()