import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="nk***777",
  database="agripredict"
)

print("Connected Successfully!")