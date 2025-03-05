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

SHEET = get_or_create_customer_sheet()

# Ensure "Ticket_Sales" sheet exists
def get_or_create_ticket_sheet():
    try:
        return GC.open("CRM_Logger").worksheet("Ticket_Sales")
    except gspread.exceptions.WorksheetNotFound:
        sheet = GC.open("CRM_Logger").add_worksheet(title="Ticket_Sales", rows="100", cols="6")
        sheet.append_row(["Date", "Customer Name", "Ticket Type", "Payment Method", "Amount Paid", "Event Name"])
        return sheet

TICKET_SHEET = get_or_create_ticket_sheet()

# Streamlit Authentication
USER_CREDENTIALS = {"admin": "password123"}  # Change this later for security

# Function to verify login
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

# Logout button
def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.sidebar.success("✅ Logged out successfully!")
        st.rerun()

st.sidebar.write(f"👤 Logged in as: {st.session_state['username']}")
logout()

# Load customer interactions from Google Sheets
def load_data():
    data = SHEET.get_all_records()
    return pd.DataFrame(data)

# Load ticket sales data from Google Sheets
def load_ticket_data():
    data = TICKET_SHEET.get_all_records()
    return pd.DataFrame(data)

# Save new interaction to Google Sheets
def save_data(name, contact, customer_type, company, preferred_contact, last_interaction, follow_up, notes):
    df = load_data()
    existing_names = df["Customer Name"].values if not df.empty else []
    if name in existing_names:
        row_idx = df.index[df["Customer Name"] == name][0] + 2  # Google Sheets is 1-based index
        SHEET.update_cell(row_idx, 10, int(df.loc[df["Customer Name"] == name, "Total Visits"].values[0]) + 1)
    else:
        new_entry = [
            datetime.now().strftime("%Y-%m-%d %H:%M"), name, contact, customer_type,
            company, preferred_contact, last_interaction.strftime("%Y-%m-%d"),
            follow_up.strftime("%Y-%m-%d"), notes, 1
        ]
        SHEET.append_row(new_entry)

# Save new ticket sale to Google Sheets
def save_ticket_sale(date, customer_name, ticket_type, payment_method, amount_paid, event_name):
    new_entry = [date, customer_name, ticket_type, payment_method, amount_paid, event_name]
    TICKET_SHEET.append_row(new_entry)

# Streamlit App UI
st.title("🎭 Teatro Las Máscaras CRM Logger")
st.write("Log customer interactions and track ticket sales.")

# Use tabs for better navigation
tab1, tab2, tab3, tab4 = st.tabs(["📋 Customer Log", "🔍 Search & Filter", "⏰ Follow-ups", "🎟 Ticket Sales"])

with tab1:
    with st.expander("📝 Log New Customer Interaction", expanded=True):
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

with tab2:
    st.subheader("🔍 Search & Filter Customers")
    search_query = st.text_input("Search by Name, Contact, or Company")
    df = load_data()
    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in str(row["Customer Name"]).lower() or search_query.lower() in str(row["Contact"]).lower() or search_query.lower() in str(row["Company"]).lower(), axis=1)]
    st.dataframe(df, use_container_width=True, height=400)

with tab3:
    st.subheader("⏰ Follow-up Reminders")
    today = datetime.today().strftime("%Y-%m-%d")
    df_followups = df[df["Follow-up Reminder Date"] >= today] if "Follow-up Reminder Date" in df.columns else pd.DataFrame()
    if not df_followups.empty:
        for index, row in df_followups.iterrows():
            st.write(f"**{row['Customer Name']}** - Follow-up on {row['Follow-up Reminder Date']}")
    else:
        st.info("No upcoming follow-ups.")
