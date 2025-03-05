import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime

# Load Google Credentials from Streamlit Secrets
creds_dict = st.secrets["GOOGLE_CREDENTIALS"]
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
GC = gspread.authorize(CREDS)

def get_or_create_customer_sheet():
    try:
        return GC.open("CRM_Logger").worksheet("Customer_Log")
    except gspread.exceptions.WorksheetNotFound:
        sheet = GC.open("CRM_Logger").add_worksheet(title="Customer_Log", rows="100", cols="10")
        sheet.append_row(["Date", "Customer Name", "Contact", "Customer Type", "Company", "Preferred Contact Method", "Last Interaction Date", "Follow-up Reminder Date", "Interaction Notes", "Total Visits"])
        return sheet

def get_or_create_ticket_sheet():
    try:
        return GC.open("CRM_Logger").worksheet("Ticket_Sales")
    except gspread.exceptions.WorksheetNotFound:
        sheet = GC.open("CRM_Logger").add_worksheet(title="Ticket_Sales", rows="100", cols="6")
        sheet.append_row(["Date", "Customer Name", "Ticket Type", "Payment Method", "Amount Paid", "Event Name"])
        return sheet

# Attempt to load sheets, ensuring failures do not break the app
try:
    SHEET = get_or_create_customer_sheet()
except Exception as e:
    SHEET = None
    st.error(f"❌ Could not load Customer_Log sheet: {e}")

try:
    TICKET_SHEET = get_or_create_ticket_sheet()
except Exception as e:
    TICKET_SHEET = None
    st.error(f"❌ Could not load Ticket_Sales sheet: {e}")

# Streamlit Authentication
USER_CREDENTIALS = {"admin": "password123"}  # Change this later for security

def login():
    st.sidebar.header("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.sidebar.success("✅ Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("❌ Incorrect username or password")

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
    st.stop()

def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.sidebar.success("✅ Logged out successfully!")
        st.rerun()

st.sidebar.write(f"👤 Logged in as: {st.session_state['username']}")
logout()

def load_data():
    if SHEET:
        data = SHEET.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame()

def load_ticket_data():
    if TICKET_SHEET:
        data = TICKET_SHEET.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame()

# Save functions

def save_data(name, contact, customer_type, company, preferred_contact, last_interaction, follow_up, notes):
    if SHEET:
        new_entry = [
            datetime.now().strftime("%Y-%m-%d %H:%M"), name, contact, customer_type,
            company, preferred_contact, last_interaction.strftime("%Y-%m-%d"),
            follow_up.strftime("%Y-%m-%d"), notes, 1
        ]
        SHEET.append_row(new_entry)

def save_ticket_sale(date, customer_name, ticket_type, payment_method, amount_paid, event_name):
    if TICKET_SHEET:
        new_entry = [date, customer_name, ticket_type, payment_method, amount_paid, event_name]
        TICKET_SHEET.append_row(new_entry)

# Streamlit App UI
st.title("🎭 Teatro Las Máscaras CRM Logger")
st.write("Log customer interactions and track ticket sales.")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Customer Log", "🔍 Search & Filter", "⏰ Follow-ups", "🎟 Ticket Sales"])

if SHEET:
    with tab1:
        with st.expander("📝 Log Customer Interaction", expanded=True):
            with st.form("interaction_form"):
                customer_name = st.text_input("Customer Name")
                contact = st.text_input("Contact (Email/Phone)")
                customer_type = st.selectbox("Customer Type", ["New", "Returning", "VIP"])
                company = st.text_input("Company/Organization")
                preferred_contact = st.selectbox("Preferred Contact Method", ["Email", "Phone Call", "WhatsApp", "In-Person"])
                last_interaction = st.date_input("Last Interaction Date")
                follow_up = st.date_input("Follow-up Reminder Date")
                notes = st.text_area("Interaction Notes")
                submitted = st.form_submit_button("Save Interaction")
                if submitted and customer_name:
                    save_data(customer_name, contact, customer_type, company, preferred_contact, last_interaction, follow_up, notes)
                    st.success("✅ Interaction saved successfully!")

if TICKET_SHEET:
    with tab4:
        with st.expander("🎟 Log Ticket Sales", expanded=True):
            with st.form("ticket_form"):
                date = st.date_input("Date of Purchase")
                customer_name = st.text_input("Customer Name (Leave blank for anonymous sales)")
                ticket_type = st.selectbox("Ticket Type", ["General", "VIP", "Student Discount"]) 
                payment_method = st.selectbox("Payment Method", ["Tix.do", "Cash at Door", "Bank Deposit"])
                amount_paid = st.number_input("Amount Paid", min_value=0.0, format="%.2f")
                event_name = st.text_input("Event Name")
                submitted = st.form_submit_button("Save Ticket Sale")
                if submitted:
                    save_ticket_sale(date.strftime("%Y-%m-%d"), customer_name if customer_name else "Anonymous", ticket_type, payment_method, amount_paid, event_name)
                    st.success("✅ Ticket sale logged successfully!")
