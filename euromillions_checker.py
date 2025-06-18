import streamlit as st
import csv
import os

st.set_page_config(page_title="EuroMillions Checker", layout="centered")
st.title("🎟️ EuroMillions Ticket Checker")

# Ticket input
input_method = st.radio("Choose input method:", ["Paste tickets", "Upload file"])

tickets = []

def parse_ticket(line):
    try:
        parts = line.strip().split("+")
        main = sorted([int(x) for x in parts[0].strip().split()])
        stars = sorted([int(x) for x in parts[1].strip().split()])
        return (main, stars)
    except:
        return None

if input_method == "Paste tickets":
    user_input = st.text_area("Paste tickets (format: 5 11 22 34 50 + 2 9)", height=150)
    if user_input:
        tickets = [parse_ticket(line) for line in user_input.strip().splitlines() if parse_ticket(line)]

else:
    uploaded_file = st.file_uploader("Upload your ticket_list.txt file", type="txt")
    if uploaded_file:
        lines = uploaded_file.read().decode("utf-8").splitlines()
        tickets = [parse_ticket(line) for line in lines if parse_ticket(line)]

# Run checker
if tickets and st.button("🔍 Check Tickets"):
    found = False
    with st.spinner("Searching..."):
        for file in sorted(os.listdir("combinations_chunked")):
            if file.endswith(".csv"):
                with open(os.path.join("combinations_chunked", file), newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        combo_main = sorted([int(row[f"Main{i}"]) for i in range(1, 6)])
                        combo_star = sorted([int(row["Star1"]), int(row["Star2"])])

                        for main, stars in tickets:
                            if main == combo_main and stars == combo_star:
                                st.success(f"🎯 Match: {main} + {stars} → in {file}")
                                found = True
    if not found:
        st.error("❌ No matches found.")
