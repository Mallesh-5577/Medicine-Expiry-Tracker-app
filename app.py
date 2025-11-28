import streamlit as st
from datetime import datetime
import sqlite3

IMAGE_FILE = "healthcare-services-annual-health-checkup-heart-rate-pulse-measurement-pills-antibiotics-dna-diseases-genes-illustration-on-light-blue-hexagonal-background-health-and-medicine-concept-vector.jpg"

# Advanced CSS for full background
page_bg_img = f"""
<style>
.stApp {{
    background-image: url('{IMAGE_FILE}');
    background-size: cover;
    background-attachment: fixed;
    background-repeat: no-repeat;
    background-position: center;
}}
.main {{
    background: rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem auto;
    box-shadow: 0 8px 22px rgba(19, 92, 152, 0.15);
}}
h1, h2, h3 {{
    text-align: center;
    color: #097eae;
    text-shadow: 1px 2px 8px #ffffff;
}}
.stTextInput>div>input, .stDateInput>div>input, .stNumberInput>div>input {{
    border-radius: 8px;
    font-size: 1.1rem;
    padding: 0.5rem 1rem;
}}
.stButton>button {{
    background: linear-gradient(90deg, #097eae 30%, #c0efff 100%);
    color: #fff;
    border-radius: 10px;
    font-weight: bold;
    font-size: 1.1rem;
    box-shadow: 0 3px 8px rgba(0,0,0,0.08);
}}
.stButton>button:hover {{
    background: #05455e;
}}
.medicine-entry {{
    background: rgba(255, 255, 255, 0.82);
    border-radius: 14px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    font-size: 1.12rem;
    box-shadow: 0 4px 12px rgba(9,126,174,0.08);
}}
.expired {{
    color: #d20606;
    font-weight: bold;
}}
.expiring-soon {{
    color: #f1c40f;
    font-weight: bold;
}}
</style>
"""

# Apply background
st.markdown(page_bg_img, unsafe_allow_html=True)


# Database setup
def init_db():
    conn = sqlite3.connect("medicine_expiry.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, batch TEXT, 
            expiry DATE, barcode TEXT, quantity INTEGER
        )
    """)
    conn.commit()
    return conn


def add_medicine(conn, name, batch, expiry, barcode, quantity):
    c = conn.cursor()
    c.execute(
        "INSERT INTO medicines (name, batch, expiry, barcode, quantity) VALUES (?, ?, ?, ?, ?)",
        (name, batch, expiry, barcode, quantity),
    )
    conn.commit()


def get_medicines(conn):
    c = conn.cursor()
    c.execute(
        "SELECT id, name, batch, expiry, barcode, quantity FROM medicines ORDER BY expiry"
    )
    return c.fetchall()


def delete_medicine(conn, med_id):
    c = conn.cursor()
    c.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
    conn.commit()


conn = init_db()

# App UI over background
st.markdown("<h1>Medicine Expiry Tracker</h1>", unsafe_allow_html=True)
st.markdown(
    """
<h3>
Welcome to the Medicine Expiry Tracker!  
This app helps you keep track of expiry dates for your medicines.  
Enter medicine details and get a reminder before expiry.

</h3>
""",
    unsafe_allow_html=True,
)

with st.form("add_medicine_form"):
    name = st.text_input("Medicine Name")
    batch = st.text_input("Batch Number")
    expiry = st.date_input("Expiry Date", min_value=datetime.today())
    barcode = st.text_input("Barcode Number")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    submitted = st.form_submit_button("Add Medicine")
    if submitted:
        if not name:
            st.warning("Please enter medicine name.")
        else:
            add_medicine(
                conn, name, batch, expiry.strftime("%Y-%m-%d"), barcode, quantity
            )
            st.success(f"Medicine '{name}' added successfully!")

meds = get_medicines(conn)
if meds:
    st.markdown("### Your Medicines")
    for med in meds:
        id_, name, batch, expiry_date, barcode, quantity = med
        expiry_dt = datetime.strptime(expiry_date, "%Y-%m-%d")
        days_left = (expiry_dt - datetime.today()).days
        status_class = ""
        status_text = ""
        if days_left < 0:
            status_text = "Expired"
            status_class = "expired"
        elif days_left <= 30:
            status_text = "Expiring Soon"
            status_class = "expiring-soon"
        st.markdown(
            f'''
            <div class="medicine-entry">
                <strong>{name}</strong><br>
                Batch: {batch}, Barcode: {barcode}, Qty: {quantity}<br>
                Expiry Date: {expiry_date} | Days left: {days_left} <span class="{status_class}">{status_text}</span>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        if st.button(f"Delete {name}", key=f"del_{id_}"):
            delete_medicine(conn, id_)
            st.experimental_rerun()
else:
    st.info("No medicines added yet. Please use the form above to add medicines.")
