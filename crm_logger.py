import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File to store customer interactions
DATA_FILE = "crm_data.csv"

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

# Initialize the CSV file if it doesn't exist
def initialize_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["Date", "Customer Name", "Contact", "Customer Type", "Company", "Preferred Contact Method", "Last Interaction Date", "Follow-up Reminder Date", "Interaction Notes"])
        df.to_csv(DATA_FILE, index=False)

# Load customer interactions
def load_data():
    return pd.read_csv(DATA_FILE) if os.path.exists(DATA_FILE) else pd.DataFrame(columns=["Date", "Customer Name", "Contact", "Customer Type", "Company", "Preferred Contact Method", "Last Interaction Date", "Follow-up Reminder Date", "Interaction Notes"])

# Save new interaction
def save_data(name, contact, customer_type, company, preferred_contact, last_interaction, follow_up, notes):
    df = load_data()
    new_entry = pd.DataFrame({
        "Date": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")],
        "Customer Name": [name],
        "Contact": [contact],
        "Customer Type": [customer_type],
        "Company": [company],
        "Preferred Contact Method": [preferred_contact],
        "Last Interaction Date": [last_interaction],
        "Follow-up Reminder Date": [follow_up],
        "Interaction Notes": [notes]
    })
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Initialize data file
initialize_data()

# Streamlit App UI
st.title("🎭 Teatro Las Máscaras CRM Logger")
st.write("Log customer interactions quickly and efficiently.")

# Layout for input form and search
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("📝 Log New Interaction")
    with st.form("interaction_form"):
        customer_name = st.text_input("Customer Name")
        contact = st.text_input("Contact (Email/Phone)")
        customer_type = st.selectbox("Customer Type", ["New", "Returning", "VIP"])
        company = st.text_input("Company/Organization")
        preferred_contact = st.selectbox("Preferred Contact Method", ["Email", "Phone Call", "WhatsApp", "In-Person"])
        last_interaction = st.date_input("Last Interaction Date")
        follow_up = st.date_input("Follow-up Reminder Date")
        notes = st.text_area("Interaction Notes")
        submitted = st.form_submit_button("Save Interaction", use_container_width=True)
        
        if submitted and customer_name:
            save_data(customer_name, contact, customer_type, company, preferred_contact, last_interaction, follow_up, notes)
            st.success("✅ Interaction saved successfully!")

with col2:
    st.subheader("🔍 Search Customer Interactions")
    search_query = st.text_input("Search by Customer Name, Contact, or Company")
    
    # Load and filter data
    df = load_data()
    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in str(row["Customer Name"]).lower() or search_query.lower() in str(row["Contact"]).lower() or search_query.lower() in str(row["Company"]).lower(), axis=1)]
    
    # Display filtered results
    st.subheader("📋 Customer Interaction History")
    st.dataframe(df, use_container_width=True, height=400)
    
    # Show upcoming follow-ups
    st.subheader("⏰ Follow-up Reminders")
    today = datetime.today().strftime("%Y-%m-%d")
    df_followups = df[df["Follow-up Reminder Date"] >= today]
    if not df_followups.empty:
        st.dataframe(df_followups, use_container_width=True, height=200)
    else:
        st.info("No upcoming follow-ups.")
    
    # Export to CSV option
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Data as CSV", csv, "crm_data.csv", "text/csv", use_container_width=True)
