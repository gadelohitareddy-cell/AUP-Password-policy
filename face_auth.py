import face_recognition
import cv2
import sqlite3
import os

# =========================
# LOAD DATABASE IMAGES
# =========================
conn = sqlite3.connect("employee.db")
cursor = conn.cursor()

cursor.execute("SELECT name, photo_path FROM employees")
users = cursor.fetchall()

known_encodings = []
known_names = []

for user in users:

    name = user[0]
    image_path = user[1]

    if os.path.exists(image_path):

        image = face_recognition.load_image_file(image_path)

        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:

            known_encodings.append(encodings[0])
            known_names.append(name)

conn.close()

print("Database faces loaded successfully")

# =========================
# OPEN CAMERA
# =========================
video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("Camera not opening")
    exit()

print("Camera started successfully")

while True:

    ret, frame = video_capture.read()

    if not ret:
        print("Failed to capture frame")
        break

    rgb_frame = frame[:, :, ::-1]

    face_locations = face_recognition.face_locations(rgb_frame)

    face_encodings = face_recognition.face_encodings(
        rgb_frame,
        face_locations
    )

    for face_encoding in face_encodings:

        matches = face_recognition.compare_faces(
            known_encodings,
            face_encoding
        )

        name = "Face Not Found"

        if True in matches:

            first_match_index = matches.index(True)

            name = known_names[first_match_index]

            cv2.putText(
                frame,
                f"Attendance Marked: {name}",
                (20,50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2
            )

        else:

            cv2.putText(
                frame,
                "Face Not Found",
                (20,50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,0,255),
                2
            )

    cv2.imshow("Face Authentication", frame)

    # PRESS Q TO EXIT
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()