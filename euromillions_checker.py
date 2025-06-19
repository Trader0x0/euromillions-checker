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

# Download and extract zip from Drive
def download_and_extract(name, link):
    zip_path = os.path.join(tempfile.gettempdir(), name)
    if not os.path.exists(zip_path):
        with urllib.request.urlopen(link) as response, open(zip_path, 'wb') as out_file:
            out_file.write(response.read())

    temp_dir = tempfile.TemporaryDirectory()
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(temp_dir.name)
    return temp_dir

# Google Drive direct links (converted from share links)
links = [
    "https://drive.google.com/uc?export=download&id=1_5BrrdMC0wnNkH0P57hJS-nhIcIYcHit",  # part1
    "https://drive.google.com/uc?export=download&id=1RMJDLwyydRse4xuviYtzqs_K06FChiah"   # part2
]

# Run checker
if tickets:
    matches = []
    for link in links:
        with st.spinner(f"📂 Downloading & scanning {link}..."):
            extracted = download_and_extract("combo_chunk.zip", link)
            for file in os.listdir(extracted.name):
                if file.endswith(".csv"):
                    with open(os.path.join(extracted.name, file), newline='') as csvfile:
                        reader = csv.reader(csvfile)
                        for row in reader:
                            combo_main = sorted(map(int, row[:5]))
                            combo_stars = sorted(map(int, row[5:]))
                            for ticket_main, ticket_stars in tickets:
                                if combo_main == ticket_main and combo_stars == ticket_stars:
                                    matches.append((ticket_main, ticket_stars, file))
    if matches:
        st.success("✅ MATCH FOUND!")
        for match in matches:
            st.write(f"🎯 {match[0]} + {match[1]} → in {match[2]}")
    else:
        st.error("❌ No matches found.")
