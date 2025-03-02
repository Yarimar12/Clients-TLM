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
        df = pd.DataFrame(columns=["Date", "Customer Name", "Contact", "Customer Type", "Company", "Preferred Contact Method", "Last Interaction Date", "Follow-up Reminder Date", "Interaction Notes", "Total Visits"])
        df.to_csv(DATA_FILE, index=False)

# Load customer interactions
def load_data():
    return pd.read_csv(DATA_FILE) if os.path.exists(DATA_FILE) else pd.DataFrame(columns=["Date", "Customer Name", "Contact", "Customer Type", "Company", "Preferred Contact Method", "Last Interaction Date", "Follow-up Reminder Date", "Interaction Notes", "Total Visits"])

# Save new interaction
def save_data(name, contact, customer_type, company, preferred_contact, last_interaction, follow_up, notes):
    df = load_data()
    if name in df["Customer Name"].values:
        df.loc[df["Customer Name"] == name, "Total Visits"] += 1
    else:
        new_entry = pd.DataFrame({
            "Date": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")],
            "Customer Name": [name],
            "Contact": [contact],
            "Customer Type": [customer_type],
            "Company": [company],
            "Preferred Contact Method": [preferred_contact],
            "Last Interaction Date": [last_interaction],
            "Follow-up Reminder Date": [follow_up],
            "Interaction Notes": [notes],
            "Total Visits": [1]
        })
        df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Initialize data file
initialize_data()

# Streamlit App UI
st.title("🎭 Teatro Las Máscaras CRM Logger")
st.write("Log customer interactions quickly and efficiently.")

# Use tabs for better navigation
tab1, tab2, tab3 = st.tabs(["📋 Customer Log", "🔍 Search & Filter", "⏰ Follow-ups"])

with tab1:
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

with tab2:
    st.subheader("🔍 Search, Filter & Sort Customer Interactions")
    search_query = st.text_input("Search by Customer Name, Contact, or Company")
    sort_by = st.selectbox("Sort by", ["Date", "Customer Name", "Last Interaction Date", "Follow-up Reminder Date", "Total Visits"], index=0)
    customer_type_filter = st.multiselect("Filter by Customer Type", ["New", "Returning", "VIP"], default=[])
    
    # Load and filter data
    df = load_data()
    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in str(row["Customer Name"]).lower() or search_query.lower() in str(row["Contact"]).lower() or search_query.lower() in str(row["Company"]).lower(), axis=1)]
    
    if customer_type_filter:
        df = df[df["Customer Type"].isin(customer_type_filter)]
    
    df = df.sort_values(by=sort_by, ascending=True)
    
    st.dataframe(df, use_container_width=True, height=400)

with tab3:
    st.subheader("⏰ Follow-up Reminders")
    today = datetime.today().strftime("%Y-%m-%d")
    df_followups = df[df["Follow-up Reminder Date"] >= today]
    if not df_followups.empty:
        for index, row in df_followups.iterrows():
            st.write(f"**{row['Customer Name']}** - Follow-up on {row['Follow-up Reminder Date']}")
            if st.button(f"✅ Mark as Completed {row['Customer Name']}", key=index):
                df.at[index, "Follow-up Reminder Date"] = "Completed"
                df.to_csv(DATA_FILE, index=False)
                st.experimental_rerun()
    else:
        st.info("No upcoming follow-ups.")
    
    # Export to CSV option
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Data as CSV", csv, "crm_data.csv", "text/csv", use_container_width=True)
