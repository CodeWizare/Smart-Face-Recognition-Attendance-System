import cv2
import face_recognition
import pickle
import os
import cloudinary
import cloudinary.uploader
from pymongo import MongoClient

# Cloudinary Configuration
cloudinary.config(
    cloud_name="ddofo7ovx",
    api_key="276577473458973",
    api_secret="tYfskoc9dKLLSz85f6Jlkkwz29o"
)

# MongoDB Configuration
client = MongoClient("mongodb+srv://<username>:<p>@cluster0.mongodb.net/?retryWrites=true&w=majority")
db = client["attendance_db"]
collection = db["students"]

# Importing student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentIds = []
for path in pathList:
    img = cv2.imread(os.path.join(folderPath, path))
    imgList.append(img)
    student_id = os.path.splitext(path)[0]
    studentIds.append(student_id)

    fileName = f'{folderPath}/{path}'
    response = cloudinary.uploader.upload(fileName, folder="students_images/")
    image_url = response['secure_url']

    collection.update_one({"id": student_id}, {"$set": {"image_url": image_url}}, upsert=True)

print(studentIds)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
