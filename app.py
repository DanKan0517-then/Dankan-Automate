from flask import Flask, render_template, request, redirect, url_for, flash
import os

from database import init_db, register_user, get_user_by_email, get_taken_vaccines, update_user_vaccines
from vaccine_logic import calculate_vaccinations, get_all_vaccines
from scheduler import start_scheduler
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super_secret_vaccine_key_123")

# Initialize excel file on startup
all_vaccines = get_all_vaccines()
init_db(all_vaccines)

# Start background scheduler
start_scheduler()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")
        email = request.form.get("email").strip().lower()
        
        if action == "login":
            user = get_user_by_email(email)
            if user:
                return redirect(url_for("dashboard", email=email))
            else:
                flash("Email not found. Please register below.", "error")
                return redirect(url_for("index"))
                
        elif action == "register":
            name = request.form.get("name")
            dob = request.form.get("dob")
            blood_group = request.form.get("blood_group")
            state = request.form.get("state")
            city = request.form.get("city")
            taken_vaccines = request.form.getlist("vaccines")
            
            from database import register_user
            register_user(email, name, dob, blood_group, state, city, taken_vaccines, all_vaccines)
            
            # Send welcome email
            try:
                schedule = calculate_vaccinations(str(dob), taken_vaccines, {})
                upcoming_vaccines = [s for s in schedule if s['status'] in ['Due', 'Upcoming']]
                from email_service import send_welcome_email
                send_welcome_email(email, name, upcoming_vaccines)
            except Exception as e:
                import logging
                logging.error(f"Welcome email error: {e}")

            flash("Registration successful! Welcome to your digital health card.", "success")
            return redirect(url_for("dashboard", email=email))

    return render_template("index.html", all_vaccines=all_vaccines)

@app.route("/dashboard/<email>")
def dashboard(email):
    user = get_user_by_email(email)
    if not user:
        return redirect(url_for('index'))
        
    taken_vaccines = get_taken_vaccines(email, all_vaccines)
    from database import get_booked_vaccines
    booked_vaccines = get_booked_vaccines(email, all_vaccines)
    dob = user.get("DOB")
    
    schedule = calculate_vaccinations(str(dob), taken_vaccines, booked_vaccines)
    
    # Simple summary stats
    taken_count = len([s for s in schedule if s['status'] == 'Taken'])
    due_count = len([s for s in schedule if s['status'] == 'Due'])
    upcoming_count = len([s for s in schedule if s['status'] == 'Upcoming' or s['status'] == 'Booked'])
    
    return render_template("dashboard.html", 
                           user=user, 
                           schedule=schedule, 
                           all_vaccines=all_vaccines,
                           taken_count=taken_count,
                           due_count=due_count,
                           upcoming_count=upcoming_count)

@app.route("/update_vaccines", methods=["POST"])
def update_vaccines():
    email = request.form.get("email")
    newly_taken_list = request.form.getlist("vaccines")
    
    # Identify which ones are NEWLY marked
    user = get_user_by_email(email)
    old_taken = get_taken_vaccines(email, all_vaccines)
    
    if update_user_vaccines(email, newly_taken_list, all_vaccines):
        flash("Vaccination schedule updated.", "success")
        
        # Determine genuinely new checkboxes
        actually_new = [v for v in newly_taken_list if v not in old_taken]
        
        if actually_new and user:
            name = user.get("Name", "User")
            dob = user.get("DOB")
            
            # Recalculate upcoming schedule since lists are updated
            current_taken = get_taken_vaccines(email, all_vaccines)
            from database import get_booked_vaccines
            current_booked = get_booked_vaccines(email, all_vaccines)
            schedule = calculate_vaccinations(str(dob), current_taken, current_booked)
            upcoming = [s for s in schedule if s['status'] in ['Due', 'Upcoming']]
            
            try:
                from email_service import send_completion_email
                send_completion_email(email, name, actually_new, upcoming)
            except Exception as e:
                import logging
                logging.error(f"Completion email error: {e}")
                
    else:
        flash("Error updating records.", "error")
        
    return redirect(url_for("dashboard", email=email))

@app.route("/book_slot", methods=["POST"])
def book_slot():
    from database import book_vaccine_slot
    email = request.form.get("email")
    vaccine_name = request.form.get("vaccine_name")
    location = request.form.get("location")
    date = request.form.get("date")
    
    if book_vaccine_slot(email, vaccine_name, location, date):
        flash(f"Slot successfully booked for {vaccine_name} at {location} on {date}!", "success")
        
        # Dispatch booking confirmation email
        user = get_user_by_email(email)
        if user:
            name = user.get("Name", "User")
            try:
                from email_service import send_booking_confirmation_email
                send_booking_confirmation_email(email, name, vaccine_name, location, date)
            except Exception as e:
                import logging
                logging.error(f"Booking email error: {e}")
    else:
        flash("Failed to book slot.", "error")
        
    return redirect(url_for("dashboard", email=email))

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
