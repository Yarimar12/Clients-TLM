import streamlit as st
import pandas as pd
import os

# File to store customer interactions
DATA_FILE = "crm_data.csv"

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

# Form to input new interactions
with st.form("interaction_form"):
    customer_name = st.text_input("Customer Name")
    contact = st.text_input("Contact (Email/Phone)")
    notes = st.text_area("Interaction Notes")
    submitted = st.form_submit_button("Save Interaction")
    
    if submitted and customer_name:
        save_data(customer_name, contact, notes)
        st.success("✅ Interaction saved successfully!")

# Display logged interactions
st.subheader("📋 Customer Interaction History")
df = load_data()
st.dataframe(df)
