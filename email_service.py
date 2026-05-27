import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, filename="app_emails.log")

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SMTP_EMAIL", "your_email@gmail.com")
SENDER_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")

def generate_ics_string(name, vaccine_name, due_date):
    dtstart = datetime(due_date.year, due_date.month, due_date.day, 9, 0)
    dtend = dtstart + timedelta(hours=1)
    dtstamp = datetime.now()
    
    fmt = "%Y%m%dT%H%M%SZ"
    
    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//DanKan Automate//Automated Scheduler//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:{uuid.uuid4()}@dankanautomate.local
DTSTAMP:{dtstamp.strftime(fmt)}
DTSTART:{dtstart.strftime(fmt)}
DTEND:{dtend.strftime(fmt)}
SUMMARY:{vaccine_name} Vaccination Appointment
DESCRIPTION:Reminder for {name} to take the {vaccine_name} vaccine.
END:VEVENT
END:VCALENDAR"""

def send_alert_email(to_email, name, vaccine_name, due_date_str):
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        ics_content = generate_ics_string(name, vaccine_name, due_date).encode('utf-8')

        msg = MIMEMultipart()
        msg['Subject'] = f"Action Required: {vaccine_name} Vaccination Reminder"
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        body = f"""
        Hello {name},

        This is an automated reminder from DanKan Automate. 
        You are scheduled to take the following vaccine:
        
        Vaccine: {vaccine_name}
        Due Date: {due_date_str}

        Please make sure to get vaccinated and update your status in our system.
        We have attached a calendar invite for your convenience.

        Stay healthy!
        """
        msg.attach(MIMEText(body, 'plain'))

        part = MIMEBase('text', 'calendar', method="REQUEST", name="invite.ics")
        part.set_payload(ics_content)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="invite.ics"')
        msg.attach(part)

        if SENDER_PASSWORD != "your_app_password" and SENDER_EMAIL != "your_email@gmail.com":
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            logging.info(f"Sent actual email reminder to {to_email} for {vaccine_name}")
        else:
            logging.info(f"[MOCK EMAIL] To: {to_email} | Subject: {vaccine_name} due on {due_date_str}")
            with open("mock_emails.log", "a") as f:
                f.write(f"{datetime.now()}: [MOCK EMAIL] To {to_email} for {vaccine_name} due {due_date_str}\n")
            
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}. Error: {e}")

def send_welcome_email(to_email, name, upcoming_vaccines):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"Welcome to DanKan Automate, {name}!"
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        upcoming_text = ""
        for v in upcoming_vaccines:
            upcoming_text += f"- {v['name']} (Due: {v['due_date']})\n        "

        body = f"""
        Hello {name},

        Welcome to DanKan Automate! 
        Your health passport has been successfully created.
        
        Based on your profile, you have {len(upcoming_vaccines)} upcoming scheduled vaccines:
        
        {upcoming_text}
        
        We will automatically send you email alerts and calendar invites when any of your doses are due!
        Log in to your dashboard anytime to review your specific dates or update your status.

        Stay healthy,
        The DanKan Automate Team
        """
        msg.attach(MIMEText(body, 'plain'))

        if SENDER_PASSWORD != "your_app_password" and SENDER_EMAIL != "your_email@gmail.com":
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            logging.info(f"Sent actual welcome email to {to_email}")
        else:
            logging.info(f"[MOCK EMAIL] Welcome email logged for {to_email}")
            
    except Exception as e:
        logging.error(f"Failed to send welcome email to {to_email}. Error: {e}")

def send_completion_email(to_email, name, new_vaccines, upcoming_vaccines):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"Vaccination Updated: Good Job, {name}!"
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        upcoming_text = ""
        for v in upcoming_vaccines:
            upcoming_text += f"- {v['name']} (Due: {v['due_date']})\n        "

        new_vax_str = ", ".join(new_vaccines)
        
        body = f"""
        Hello {name},

        Good job! We have updated your DanKan Automate profile.
        You successfully marked the following vaccine(s) as completed:
        - {new_vax_str}
        
        Here is a quick reminder of your remaining scheduled vaccines:
        
        {upcoming_text}
        
        Keep up the great work staying healthy!

        Best,
        The DanKan Automate Team
        """
        msg.attach(MIMEText(body, 'plain'))

        if SENDER_PASSWORD != "your_app_password" and SENDER_EMAIL != "your_email@gmail.com":
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            logging.info(f"Sent completion email to {to_email}")
        else:
            logging.info(f"[MOCK EMAIL] Completion logged for {to_email}")
            
    except Exception as e:
        logging.error(f"Failed to send completion email to {to_email}. Error: {e}")

def send_booking_confirmation_email(to_email, name, vaccine_name, location, date):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"Action Required: {vaccine_name} Slot Confirmed!"
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        body = f"""
        Hello {name},

        Your vaccination slot for {vaccine_name} has been successfully booked!
        
        📅 Date: {date}
        🏥 Location: {location}
        
        Brief info regarding {vaccine_name}:
        This required vaccination defends against dangerous preventable diseases and helps keep community immunity high. Please make sure to arrive on time and update the system once complete.

        Stay healthy,
        The DanKan Automate Team
        """
        msg.attach(MIMEText(body, 'plain'))

        if SENDER_PASSWORD != "your_app_password" and SENDER_EMAIL != "your_email@gmail.com":
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            logging.info(f"Sent booking confirmation email to {to_email}")
        else:
            logging.info(f"[MOCK EMAIL] Booking confirmed for {to_email} at {location} on {date}")
            
    except Exception as e:
        logging.error(f"Failed to send booking confirmation email to {to_email}. Error: {e}")
