import streamlit as st
import csv
import os
import zipfile
import tempfile

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

# Upload multiple ZIPs
uploaded_zips = st.file_uploader("Upload one or more combinations ZIP files (max 200MB each)", type="zip", accept_multiple_files=True)

if tickets and uploaded_zips:
    found = False
    match_count = 0
    matched_lines = []

    with st.spinner("🔍 Scanning uploaded files..."):
        for uploaded_zip in uploaded_zips:
            with tempfile.TemporaryDirectory() as tmpdirname:
                with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
                    zip_ref.extractall(tmpdirname)

                for file in sorted(os.listdir(tmpdirname)):
                    if file.endswith(".csv"):
                        with open(os.path.join(tmpdirname, file), newline="") as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                combo_main = sorted([int(row[f"Main{i}"]) for i in range(1, 6)])
                                combo_star = sorted([int(row["Star1"]), int(row["Star2"])])

                                for main, stars in tickets:
                                    if main == combo_main and stars == combo_star:
                                        msg = f"🎯 Match: {main} + {stars} → in `{file}`"
                                        matched_lines.append(msg)
                                        match_count += 1
                                        found = True

    if found:
        st.success(f"✅ Found {match_count} matching ticket(s)")
        for match in matched_lines:
            st.markdown(match)
    else:
        st.error("❌ No matches found across uploaded ZIPs.")

st.markdown("""
---
**Tip:** You can upload multiple `.zip` chunks under 200MB to search all at once.
""")
