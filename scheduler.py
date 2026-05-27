import logging
from database import get_all_users, get_taken_vaccines
from vaccine_logic import calculate_vaccinations, get_all_vaccines
from email_service import send_alert_email
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def check_and_send_reminders():
    logging.info(f"Running daily reminder check: {datetime.now()}")
    users = get_all_users()
    all_vaccine_names = get_all_vaccines()
    
    today = datetime.now().date()
    
    for user in users:
        email = user.get('Email')
        name = user.get('Name')
        dob = user.get('DOB')
        
        if not email or not dob:
            continue
            
        taken = get_taken_vaccines(email, all_vaccine_names)
        schedule = calculate_vaccinations(str(dob), taken)
        
        for v in schedule:
            # We don't remind for 'Taken'
            if v['status'] in ['Upcoming', 'Due']:
                due_date_str = v['due_date']
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                except:
                    continue
                
                # Logic: remind 7 days before, 1 day before, and ON the day.
                days_diff = (due_date - today).days
                
                # Remind on these specific marks
                if days_diff in [7, 1, 0]:
                    send_alert_email(email, name, v['name'], due_date_str)

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run once a day at 9 AM
    scheduler.add_job(check_and_send_reminders, 'cron', hour=9, minute=0)
    scheduler.start()
    logging.info("Scheduler started. Background tasks are running.")
