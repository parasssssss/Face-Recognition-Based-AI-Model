import face_recognition
import os
import pickle

dataset_path = "dataset/known"
encodings = []
names = []

for file in os.listdir(dataset_path):
    img = face_recognition.load_image_file(f"{dataset_path}/{file}")
    encoding = face_recognition.face_encodings(img)[0]
    encodings.append(encoding)
    names.append(os.path.splitext(file)[0])

# Save encodings
with open("encodings.pkl", "wb") as f:
    pickle.dump((encodings, names), f)

print("✅ Encodings saved! Now run security_system.py")
