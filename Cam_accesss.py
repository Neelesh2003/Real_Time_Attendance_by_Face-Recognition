import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
'databaseURL':"https://facerecognition-attendance-default-rtdb.firebaseio.com/",
'storageBucket': "facerecognition-attendance.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640) 
cap.set(4, 480)  
imgBackground = cv2.imread('Background/back_img.png')
folderModePath='Background\modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
print("Loaded Encode File........!")     

file = open('EncodeFile.p', 'rb')   
encodeListKnownwithID = pickle.load(file)
file.close()
encodeListKnown,studentId = encodeListKnownwithID
print(studentId)
print("Encode File Loaded........!")  

modeType = 0
counter = 0
id = -1
ImgStudent = []


while True:
   
    success, frame = cap.read()
    imgS = cv2.resize(frame,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgS)
    encodeCurrentFrame = face_recognition.face_encodings(imgS,faceCurrentFrame)
  
    imgBackground[170:170+480, 55:55+640] = frame
    imgBackground[95:95+523, 848:848+350] = imgModeList[modeType]
    
    if faceCurrentFrame :
        for encodeFace, faceLoc in zip(encodeCurrentFrame,faceCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        #print("matches", matches)
        #print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
        #print("matchIndex",matchIndex)

            if matches[matchIndex]:
            #print("known face Detected")
           # print(studentId[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1,x2,y2,x1 =  y1 * 4, x2 * 4, y2 * 4, x1 * 4 
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=1)
                id = studentId[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(275,400))
                    cv2.imshow('Face Attendance', imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
        if counter!= 0:
        

            if counter == 1:
                studentInfo = db.reference(f'student/{id}').get()
                print(studentInfo)

                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                ImgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2RGB)

                #update attance 
                ref = db.reference(f'student/{id}')
                
                studentInfo['total_attendance'] += 1
                ref.child('total_attendance').set( studentInfo['total_attendance'])

            #  Update date and time

                dateTimeobject = datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")

                                                
                secondsElapsed = (datetime.now()-dateTimeobject).total_seconds()
                print(secondsElapsed)

                if secondsElapsed>30:        

                    ref = db.reference(f'student/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set( studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
                else:
                    modeType = 3
                    counter = 0
                imgBackground[95:95+523, 848:848+350] = imgModeList[modeType]

            if modeType != 3:

            
                if 10<counter<20:    
                        modeType = 2

                imgBackground[95:95+523, 848:848+350] = imgModeList[modeType]

                if counter<=10:
                    cv2.putText(imgBackground,str(studentInfo['total_attendance']),(886,155),
                                cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),1)
                    cv2.putText(imgBackground,str(studentInfo['Major']),(1022,516),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                    cv2.putText(imgBackground,str(id),(1025,468),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                    cv2.putText(imgBackground,str(studentInfo['standing']),(936,582),
                                cv2.FONT_HERSHEY_COMPLEX,0.66,(0,0,0),1)
                    cv2.putText(imgBackground,str(studentInfo['year']),(1032,582),
                                cv2.FONT_HERSHEY_COMPLEX,0.66,(0,0,0),1)
                    cv2.putText(imgBackground,str(studentInfo['Starting-Year']),(1115,582),
                                cv2.FONT_HERSHEY_COMPLEX,0.66,(0,0,0),1)
                    (w, h), _ = cv2.getTextSize(studentInfo['Name'],
                                cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (350-w)//2
                    cv2.putText(imgBackground,str(studentInfo['Name']),(890+offset,425),
                                cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,0),1)                                  
            
                    imgBackground[175:175+216,916:916+216] = ImgStudent      
                counter += 1   

                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    ImgStudent = []
                    imgBackground[95:95+523, 848:848+350] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0    

    #cv2.imshow('Camera', frame)
    cv2.imshow('Face Attendance', imgBackground)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
