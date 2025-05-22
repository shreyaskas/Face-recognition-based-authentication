from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

def speak(text):
    speaker = Dispatch("SAPI.SpVoice")
    speaker.Speak(text)

# Initialize webcam and face detector
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

# Load faces and labels
with open('data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

LABELS = np.array(LABELS)

# Trim to same length
min_length = min(len(FACES), len(LABELS))
FACES = FACES[:min_length]
LABELS = LABELS[:min_length]

print('Shape of Faces matrix -->', FACES.shape)

IMG_WIDTH = int(np.sqrt(FACES.shape[1] / 3))  
IMG_HEIGHT = int(FACES.shape[1] / (3 * IMG_WIDTH))

print(f"Expected Image Dimensions: {IMG_WIDTH}x{IMG_HEIGHT}")

# Train KNN model
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Background image
imgBackground = cv2.imread("background.png")

# Attendance variables
COL_NAMES = ['NAME', 'TIME']
attendance_list = []  # to track already marked names

# Create CapturedFaces folder if not exists
if not os.path.exists('CapturedFaces'):
    os.makedirs('CapturedFaces')

# Setup current date
date = datetime.now().strftime("%d-%m-%Y")

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w]
        crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY) if FACES.shape[1] % 3 != 0 else crop_img
        resized_img = cv2.resize(crop_img_gray, (IMG_WIDTH, IMG_HEIGHT)).flatten().reshape(1, -1)

        if resized_img.shape[1] != FACES.shape[1]:
            continue

        output = knn.predict(resized_img)

        recognized_name = str(output[0])

        # Draw rectangle and show name
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
        cv2.putText(frame, recognized_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 255), 2)

        # Mark attendance only once per person
        if recognized_name not in attendance_list:
            attendance_list.append(recognized_name)
            current_time = datetime.now().strftime("%H:%M:%S")
            with open(f"Attendance/Attendance_{date}.csv", "a", newline='') as csvfile:
                writer = csv.writer(csvfile)
                if os.stat(f"Attendance/Attendance_{date}.csv").st_size == 0:
                    writer.writerow(COL_NAMES)  # write header if file empty
                writer.writerow([recognized_name, current_time])

            # Speak welcome
            speak(f"Attendance marked for {recognized_name}")
            print(f"[INFO] Attendance marked for {recognized_name} at {current_time}")

            # Save snapshot
            timestamp_img = datetime.now().strftime('%Y%m%d_%H%M%S')
            face_filename = f"CapturedFaces/{recognized_name}_{timestamp_img}.jpg"
            cropped_face = frame[y:y+h, x:x+w]
            cv2.imwrite(face_filename, cropped_face)
            print(f"[INFO] Saved snapshot for {recognized_name}")

    cv2.imshow("Attendance System", frame)

    k = cv2.waitKey(1)
    if k == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
