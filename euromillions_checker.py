import streamlit as st
import csv
import os
import zipfile
import tempfile
import urllib.request

st.set_page_config(page_title="EuroMillions Checker", layout="centered")
st.title("🎟️ EuroMillions Ticket Checker")

# --- Input selection ---
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

# --- Remote ZIPs to download ---
combo_zip_links = [
    "https://drive.google.com/uc?export=download&id=1RMJDLwyydRse4xuviYtzqs_K06FChiah",  # part 1
    "https://drive.google.com/uc?export=download&id=1_5BrrdMC0wnNkH0P57hJS-nhIcIYcHit"   # part 2
]

# --- Match Checker ---
def download_and_extract(name, link):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
            urllib.request.urlretrieve(link, tmp_zip.name)

        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(tmp_zip.name, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return temp_dir
    except zipfile.BadZipFile:
        st.error(f"❌ '{name}' is not a valid ZIP file.")
        return None

if tickets:
    st.subheader("🔍 Scanning combinations...")
    matches = []

    for idx, link in enumerate(combo_zip_links, start=1):
        zip_label = f"part{idx}.zip"
        folder = download_and_extract(zip_label, link)

        if folder:
            with st.spinner(f"Checking {zip_label}..."):
                for filename in os.listdir(folder):
                    if filename.endswith(".csv"):
                        filepath = os.path.join(folder, filename)
                        with open(filepath, newline="") as f:
                            reader = csv.reader(f)
                            for row in reader:
                                try:
                                    main = sorted([int(x) for x in row[0].split()])
                                    stars = sorted([int(x) for x in row[1].split()])
                                    for t_main, t_stars in tickets:
                                        if main == t_main and stars == t_stars:
                                            matches.append((t_main, t_stars, filename))
                                except:
                                    continue

    if matches:
        st.success("🎉 Match found!")
        for match in matches:
            st.write(f"✔️ Match: {match[0]} + {match[1]} → in `{match[2]}`")
    else:
        st.warning("❌ No matches found.")
