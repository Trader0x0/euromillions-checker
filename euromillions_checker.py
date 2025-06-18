import streamlit as st
import os
import zipfile
import csv
import requests

# URLs for your ZIP files on Google Drive
drive_links = {
    "part1": "https://drive.google.com/uc?export=download&id=1_5BrrdMC0wnNkH0P57hJS-nhIcIYcHit",
    "part2": "https://drive.google.com/uc?export=download&id=1RMJDLwyydRse4xuviYtzqs_K06FChiah"
}

chunk_folder = "euromillions_chunks"
os.makedirs(chunk_folder, exist_ok=True)

# Auto download and extract ZIP files if not already done
def download_and_extract(name, url):
    zip_path = f"{name}.zip"
    if not os.path.exists(f"{chunk_folder}/combinations_1.csv"):  # Only checks one file to confirm extract
        with st.spinner(f"Downloading {name}..."):
            r = requests.get(url)
            with open(zip_path, 'wb') as f:
                f.write(r.content)
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(chunk_folder)
        os.remove(zip_path)

for name, link in drive_links.items():
    download_and_extract(name, link)

st.set_page_config(page_title="EuroMillions Checker", layout="centered")
st.title("🎟️ EuroMillions Ticket Checker")

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

if tickets:
    found = False
    with st.spinner("🔍 Searching all tickets..."):
        for file in os.listdir(chunk_folder):
            if file.endswith(".csv"):
                with open(os.path.join(chunk_folder, file), newline='') as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        combo_main = sorted([int(x) for x in row[:5]])
                        combo_stars = sorted([int(x) for x in row[5:]])
                        for user_main, user_stars in tickets:
                            if user_main == combo_main and user_stars == combo_stars:
                                st.success(f"🎯 Match: {user_main} + {user_stars} ➜ in `{file}`")
                                found = True
    if not found:
        st.error("❌ No matches found.")
