import streamlit as st
import pandas as pd
import time
from datetime import datetime
import subprocess
import os
from PIL import Image
import zipfile
import io

from streamlit_autorefresh import st_autorefresh

# ====== Date and Time Setup ======
ts = time.time()
date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")

# ====== Streamlit Frontend Layout ======
# Top Row Layout
col1, col2, col3, col4 = st.columns([4, 2, 2, 2])

with col2:
    name_to_add = st.text_input("Enter Name", placeholder="Type Name Here")

with col3:
    if st.button("➕ Add New Face"):
        if name_to_add.strip() == "":
            st.warning("⚠️ Please enter a name!")
        else:
            with st.spinner("⌛ Capturing face..."):
                try:
                    subprocess.run(["python", "add_faces.py", name_to_add], check=True)
                    st.success(f"✅ Face added for {name_to_add}!")
                except Exception as e:
                    st.error(f"❌ Failed: {e}")

with col4:
    if st.button("🎯 Start Attendance"):
        try:
            subprocess.run(["python", "test.py"], check=True)
        except Exception as e:
            st.error(f"❌ Failed to start attendance: {e}")

# ====== Separator Line ======
st.markdown("---")

# ====== Date Selector for Attendance View ======
st.subheader("📅 View Attendance by Date")
selected_date = st.date_input("Select a Date", datetime.now())
selected_date_str = selected_date.strftime("%d-%m-%Y")

attendance_file = f"Attendance/Attendance_{selected_date_str}.csv"

# ====== Display Attendance ======
try:
    df = pd.read_csv(attendance_file)
    st.success(f"Showing Attendance for {selected_date_str}")
    st.dataframe(df.style.highlight_max(axis=0))
except FileNotFoundError:
    st.error(f"No attendance file found for {selected_date_str}.")

# ====== Separator Line ======
st.markdown("---")

# ====== Captured Faces Gallery ======
st.header("📸 Captured Faces Gallery")

# Create folder if not exists
if not os.path.exists("CapturedFaces"):
    os.makedirs("CapturedFaces")

# Load images
images = os.listdir("CapturedFaces")

# ====== Add Search Functionality ======
search_name = st.text_input("🔍 Search for a Face by Name", placeholder="Type Name Here to Search")

# Filter images by name
if search_name:
    images = [img for img in images if search_name.lower() in img.lower()]

# Display Images
if images:
    col1, col2, col3 = st.columns(3)

    for idx, image_name in enumerate(images):
        image_path = os.path.join("CapturedFaces", image_name)
        img = Image.open(image_path)

        if idx % 3 == 0:
            with col1:
                st.image(img, caption=image_name, use_column_width=True)
        elif idx % 3 == 1:
            with col2:
                st.image(img, caption=image_name, use_column_width=True)
        else:
            with col3:
                st.image(img, caption=image_name, use_column_width=True)
else:
    st.info("No captured faces found that match your search!")

# ====== Download Captured Faces as ZIP ======
if images:
    if st.button("📦 Download All Captured Faces as ZIP"):
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for img_name in images:
                img_path = os.path.join("CapturedFaces", img_name)
                zip_file.write(img_path, arcname=img_name)

        zip_buffer.seek(0)
        st.download_button(
            label="📥 Download ZIP",
            data=zip_buffer,
            file_name="CapturedFaces.zip",
            mime="application/zip"
        )
