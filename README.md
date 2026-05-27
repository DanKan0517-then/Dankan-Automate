# DanKan Automate - Automated Vaccination Management System

DanKan Automate is a vaccination management system made using Flask. It helps users track vaccines based on the IAP (Indian Academy of Pediatrics) vaccination schedule.

The system automatically calculates vaccine due dates using the user's DOB and categorizes vaccines into:

- Taken
- Due
- Upcoming
- Booked

Users can also book vaccination slots and receive automatic email reminders before vaccine due dates.

The system sends reminders:

- 7 days before
- 1 day before
- On the due date

Email reminders also include calendar invite files (.ics) so users can add them directly to calendar apps.

---

## Features

- User Registration and Login
- Vaccination tracking based on IAP schedule
- Automatic vaccine due date calculation
- Vaccine status tracking (Taken, Due, Upcoming, Booked)
- Vaccination slot booking
- Email reminders for vaccines
- Calendar invite support (.ics files)
- Daily background scheduler for reminders

---

## Vaccines Covered

This system includes common vaccines from the IAP schedule such as:

- BCG
- OPV (0–3 doses)
- Hepatitis B
- DTP + Booster
- Rotavirus
- PCV
- Measles / MR
- MMR
- Hepatitis A
- Varicella
- Typhoid Conjugate
- Flu Vaccine

---

## Project Structure

```bash
vaccination_system/

├── app.py
├── database.py
├── vaccine_logic.py
├── email_service.py
├── scheduler.py
├── requirements.txt
├── .env
├── users.xlsx

├── templates/
│   ├── index.html
│   └── dashboard.html

└── static/
    └── css/
        └── style.css
```

### File Description

- `app.py` → Main Flask app with routes and logic  
- `database.py` → Stores user data using Excel (`users.xlsx`)  
- `vaccine_logic.py` → Vaccine schedule and due date logic  
- `email_service.py` → Sends email reminders with calendar invite  
- `scheduler.py` → Runs reminder checks daily at 9 AM  

---

## Tech Stack

Backend:
- Python
- Flask
- Pandas
- OpenPyXL
- APScheduler

Frontend:
- HTML
- CSS
- Jinja2 Templates

Database:
- Excel (`.xlsx`)

Email:
- SMTP using Python

---

## Setup

### 1. Clone the project

```bash
git clone <repo-link>
cd vaccination_system
```

### 2. Create virtual environment

Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add email configuration (optional)

Inside `.env` file:

```env
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SECRET_KEY=your_secret_key
```

Use Gmail App Password instead of normal password.

### 5. Run the project

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5001
```

---

## Email Reminder System

The system checks vaccine due dates daily and sends reminders:

- 7 days before vaccine date
- 1 day before vaccine date
- On vaccine date

Each email also contains a `.ics` calendar file which can be added to Google Calendar, Apple Calendar, etc.

---

## Notes

- If email credentials are not added, the app works in mock mode and logs emails instead of sending them.
- Email logs are stored in:

```text
app_emails.log
```

- App logs are stored in:

```text
app_logs.txt
```

- Port `5001` is used to avoid conflict with macOS AirPlay.

---

##PAGE LOOK

<img width="633" height="828" alt="Screenshot 2026-05-27 at 10 49 20 AM" src="https://github.com/user-attachments/assets/6cd85d76-5f42-41f5-86b4-3865457743f2" />

