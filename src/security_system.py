import cv2
import face_recognition
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
from db_utils import insert_log
from alert_utils import play_buzzer, send_whatsapp_alert

# Load encodings
with open("encodings.pkl", "rb") as f:
    known_encodings, known_names = pickle.load(f)

# Start webcam
video = cv2.VideoCapture(0)

last_logged = {}

unknown_cache = []
UNKNOWN_THRESHOLD = 0.6 

# Time gap between logs (in seconds)
LOG_INTERVAL = 60  

def get_unknown_id(face_encoding):
    # Check similarity with existing unknowns in cache
    for enc, ts, uid in unknown_cache:
        distance = np.linalg.norm(face_encoding - enc)
        if distance < UNKNOWN_THRESHOLD:
            return uid
    # If no similar, assign new id
    new_id = str(hash(tuple(np.round(face_encoding, 5))))
    unknown_cache.append((face_encoding, datetime.now(), new_id))
    # Optional: remove old cache entries older than 10 minutes
    unknown_cache[:] = [
        (enc, ts, uid) for (enc, ts, uid) in unknown_cache
        if (datetime.now() - ts) < timedelta(minutes=10)
    ]
    return new_id

while True:
    ret, frame = video.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)

        # Default image path is None
        img_path = None

        now = datetime.now()

        if True in matches:
            match_index = np.argmin(face_distances)
            name = known_names[match_index]
            status = "Authorized"
            color = (0, 255, 0)
            label = f"Authorized: {name}"
        else:
            # Stable unknown identification
            unknown_id = get_unknown_id(face_encoding)
            name = f"Unknown_{unknown_id}"
            status = "⚠️ Intruder"
            color = (0, 0, 255)
            label = "⚠️ ALERT: Unknown!"

            # Save intruder snapshot only if not recently logged
            if name not in last_logged or (now - last_logged[name]) > timedelta(seconds=LOG_INTERVAL):
                os.makedirs("dataset/unknown", exist_ok=True)
                timestamp = now.strftime("%Y%m%d_%H%M%S")
                img_path = f"dataset/unknown/unknown_{timestamp}.jpg"
                cv2.imwrite(img_path, frame)

       
        if name not in last_logged or (now - last_logged[name]) > timedelta(seconds=LOG_INTERVAL):
            insert_log(name, status, img_path)  
            last_logged[name] = now

            if status == "⚠️ Intruder":
                play_buzzer()
                send_whatsapp_alert(f"⚠️ Intruder detected at {now.strftime('%Y-%m-%d %H:%M:%S')}!")

        # Draw box & label
        top, right, bottom, left = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow("Security Feed", frame)

    # Exit if 'q' pressed OR window closed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    if cv2.getWindowProperty("Security Feed", cv2.WND_PROP_VISIBLE) < 1:
        break

video.release()
cv2.destroyAllWindows()
print("✅ Security system stopped. Camera released and window closed.")
