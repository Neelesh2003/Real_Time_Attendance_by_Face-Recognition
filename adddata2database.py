import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
'databaseURL':"https://facerecognition-attendance-default-rtdb.firebaseio.com/"
})

ref = db.reference('student')

data = {
    "0204": 
       {
         "Name": "Neelesh Gupta",
         "Major": "Student",
         "Starting-Year":2008,
         "total_attendance":65,
         "standing":"100",
         "year":20,
         "last_attendance_time":"2021-01-21 9:11:30"
       },
    "0208": 
       {
         "Name": "Vivek Kushwaha",
         "Major": "Student",
         "Starting-Year":2013,
         "total_attendance":0,
         "standing":"15",
         "year":2023,
         "last_attendance_time":"2021-01-21 9:11:30"
       },
    "0206":
       {
         "Name": "Kathrien langford",
         "Major": "Acting",
         "Starting-Year":2002,
         "total_attendance":7,
         "standing":"4",
         "year":6,
         "last_attendance_time":"2020-12-11 00:54:34"
       },
    "0205":
       {
         "Name": "Elon mask",
         "Major": "Space-x",
         "Starting-Year":2001,
         "total_attendance":9,
         "standing":"4",
         "year":15,
         "last_attendance_time":"2019-12-11 00:55:34"
       },
    "0207":
       {
         "Name": "Mark Zugerbug",
         "Major": "facebook",
         "Starting-Year":1990,
         "total_attendance":10,
         "standing":"10",
         "year":12,
         "last_attendance_time":"2012-10-11 00:59:34"
       }      
}
for key,value in data.items():
    ref.child(key).set(value)
    