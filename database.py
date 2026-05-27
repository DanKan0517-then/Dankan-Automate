import pandas as pd
import os

DB_FILE = "users.xlsx"

def init_db(all_vaccine_names):
    if not os.path.exists(DB_FILE):
        columns = ['Email', 'Name', 'DOB', 'BloodGroup', 'State', 'City'] + all_vaccine_names
        df = pd.DataFrame(columns=columns)
        df.to_excel(DB_FILE, index=False)

def get_all_users():
    if not os.path.exists(DB_FILE):
        return []
    df = pd.read_excel(DB_FILE, dtype=str)
    df = df.fillna('')
    return df.to_dict('records')

def get_user_by_email(email):
    users = get_all_users()
    email_clean = str(email).strip().lower()
    for u in users:
        if str(u.get('Email', '')).strip().lower() == email_clean:
            return u
    return None

def register_user(email, name, dob, blood_group, state, city, taken_vaccines_list, all_vaccine_names):
    if os.path.exists(DB_FILE):
        df = pd.read_excel(DB_FILE, dtype=str)
    else:
        columns = ['Email', 'Name', 'DOB', 'BloodGroup', 'State', 'City'] + all_vaccine_names
        df = pd.DataFrame(columns=columns)

    email_clean = str(email).strip().lower()
    
    # Check if exists
    if email_clean in df['Email'].astype(str).str.lower().str.strip().values:
        idx = df.index[df['Email'].astype(str).str.lower().str.strip() == email_clean].tolist()[0]
        df.at[idx, 'Name'] = name
        df.at[idx, 'DOB'] = dob
        df.at[idx, 'BloodGroup'] = blood_group
        df.at[idx, 'State'] = state
        df.at[idx, 'City'] = city
        for v in all_vaccine_names:
            if v in taken_vaccines_list:
                df.at[idx, v] = 'Yes'
    else:
        # Append new
        new_row = {'Email': email_clean, 'Name': name, 'DOB': dob, 'BloodGroup': blood_group, 'State': state, 'City': city}
        for v in all_vaccine_names:
            new_row[v] = 'Yes' if v in taken_vaccines_list else ''
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_excel(DB_FILE, index=False)
    
def update_user_vaccines(email, recently_taken_list, all_vaccine_names):
    if not os.path.exists(DB_FILE):
        return False
        
    df = pd.read_excel(DB_FILE, dtype=str)
    email_clean = str(email).strip().lower()
    
    if email_clean in df['Email'].astype(str).str.lower().str.strip().values:
        idx = df.index[df['Email'].astype(str).str.lower().str.strip() == email_clean].tolist()[0]
        for v in recently_taken_list:
            if v in all_vaccine_names:
                df.at[idx, v] = 'Yes'
        df.to_excel(DB_FILE, index=False)
        return True
    return False

def book_vaccine_slot(email, vaccine_name, location, date):
    if not os.path.exists(DB_FILE):
        return False
    df = pd.read_excel(DB_FILE, dtype=str)
    email_clean = str(email).strip().lower()
    if email_clean in df['Email'].astype(str).str.lower().str.strip().values:
        idx = df.index[df['Email'].astype(str).str.lower().str.strip() == email_clean].tolist()[0]
        # Store booking status
        df.at[idx, vaccine_name] = f"Booked: {location} on {date}"
        df.to_excel(DB_FILE, index=False)
        return True
    return False

def get_taken_vaccines(email, all_vaccine_names):
    user = get_user_by_email(email)
    if not user:
        return []
    taken = []
    for v in all_vaccine_names:
        if str(user.get(v, '')).strip() == 'Yes':
            taken.append(v)
    return taken

def get_booked_vaccines(email, all_vaccine_names):
    user = get_user_by_email(email)
    if not user:
        return {}
    booked = {}
    for v in all_vaccine_names:
        val = str(user.get(v, '')).strip()
        if val.startswith('Booked: '):
            location_string = val.replace('Booked: ', '')
            booked[v] = location_string
    return booked
