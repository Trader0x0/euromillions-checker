import streamlit as st
import csv
import os
import zipfile
import tempfile
import urllib.request

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

# ✅ Auto-download from Google Drive if not already cached
@st.cache_resource
def download_and_extract(name, link):
    zip_path = os.path.join(tempfile.gettempdir(), name)
    if not os.path.exists(zip_path):
        with urllib.request.urlopen(link) as response, open(zip_path, 'wb') as out_file:
            out_file.write(response.read())
    extract_path = os.path.join(tempfile.gettempdir(), name.replace(".zip", ""))
    if not os.path.exists(extract_path):
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_path)
    return extract_path

# 🔗 Add your permanent zip links here
links = [
    ("combinations.part1.zip", "https://drive.google.com/uc?export=download&id=1_5BrrdMC0wnNkH0P57hJS-nhIcIYcHit"),
    ("combinations.part2.zip", "https://drive.google.com/uc?export=download&id=1RMJDLwyydRse4xuviYtzqs_K06FChiah")
]

# 🧠 Start checking
if tickets:
    import time
    found = False
    for zip_name, link in links:
        with st.spinner(f"🔍 Checking {zip_name}..."):
            folder = download_and_extract(zip_name, link)
            for filename in os.listdir(folder):
                if filename.endswith(".csv"):
                    filepath = os.path.join(folder, filename)
                    with open(filepath, newline='') as csvfile:
                        reader = csv.reader(csvfile)
                        for row in reader:
                            combo_main = sorted([int(x) for x in row[:5]])
                            combo_stars = sorted([int(x) for x in row[5:]])
                            for ticket_main, ticket_stars in tickets:
                                if ticket_main == combo_main and ticket_stars == combo_stars:
                                    st.success(f"✅ Match found: {ticket_main} + {ticket_stars} in {filename}")
                                    found = True
                                    break
                        if found:
                            break
            if found:
                break
    if not found:
        st.error("❌ No matches found.")
