import streamlit as st
import pandas as pd
import os

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
            st.sidebar.success("✅ Login successful! Please wait...")
            st.experimental_rerun()
        else:
            st.error("❌ Incorrect username or password")

if "logged_in" not in st.session_state:
    login()
    st.stop()

# Logout button
def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.sidebar.success("✅ Logged out successfully!")
        st.experimental_rerun()

st.sidebar.write(f"👤 Logged in as: {st.session_state['username']}")
logout()

# Initialize the CSV file if it doesn't exist
def initialize_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["Date", "Customer Name", "Contact", "Interaction Notes"])
        df.to_csv(DATA_FILE, index=False)

# Load customer interactions
def load_data():
    return pd.read_csv(DATA_FILE) if os.path.exists(DATA_FILE) else pd.DataFrame(columns=["Date", "Customer Name", "Contact", "Interaction Notes"])

# Save new interaction
def save_data(name, contact, notes):
    df = load_data()
    new_entry = pd.DataFrame({
        "Date": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")],
        "Customer Name": [name],
        "Contact": [contact],
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
        notes = st.text_area("Interaction Notes")
        submitted = st.form_submit_button("Save Interaction", use_container_width=True)
        
        if submitted and customer_name:
            save_data(customer_name, contact, notes)
            st.success("✅ Interaction saved successfully!")

with col2:
    st.subheader("🔍 Search Customer Interactions")
    search_query = st.text_input("Search by Customer Name or Contact")
    
    # Load and filter data
    df = load_data()
    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in str(row["Customer Name"]).lower() or search_query.lower() in str(row["Contact"]).lower(), axis=1)]
    
    # Display filtered results
    st.subheader("📋 Customer Interaction History")
    st.dataframe(df, use_container_width=True, height=400)
    
    # Export to CSV option
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Data as CSV", csv, "crm_data.csv", "text/csv", use_container_width=True)
