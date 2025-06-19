import streamlit as st
import zipfile
import tempfile
import csv
import os
import urllib.request

st.set_page_config(page_title="EuroMillions Checker", layout="centered")
st.title("🎟️ EuroMillions Ticket Checker")

# ---- TICKET INPUT ----
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

# ---- DOWNLOAD + SCAN ----
def download_and_extract(name, link):
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            zip_path = os.path.join(tmpdirname, name)
            urllib.request.urlretrieve(link, zip_path)

            found = False
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmpdirname)
                for file in os.listdir(tmpdirname):
                    if file.endswith(".csv"):
                        with open(os.path.join(tmpdirname, file), newline='') as f:
                            reader = csv.reader(f)
                            for row in reader:
                                main = sorted([int(n) for n in row[:5]])
                                stars = sorted([int(n) for n in row[5:]])
                                for user_main, user_stars in tickets:
                                    if user_main == main and user_stars == stars:
                                        st.success(f"✅ Match: {main} + {stars} → in {file}")
                                        found = True
            return found
    except zipfile.BadZipFile:
        st.error(f"❌ '{name}' is not a valid ZIP file.")
        return False

# ---- RUN ----
if tickets:
    links = {
        "chunk1.zip": "https://drive.google.com/uc?export=download&id=1_gJWdGjEqWlDPyNDesi0JXZCmY3WT8-i",
        "chunk2.zip": "https://drive.google.com/uc?export=download&id=1o4p4GAAFD4ulnSfzCSJcPA9m07trUk5q"
    }

    found_any = False
    for name, link in links.items():
        found = download_and_extract(name, link)
        if found:
            found_any = True

    if not found_any:
        st.warning("❌ No matches found.")
