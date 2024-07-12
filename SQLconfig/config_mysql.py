import mysql.connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="sofascoreBR"
)
sql = "SET GLOBAL max_allowed_packet=1073741824"
mycursor_example = mydb.cursor()
mycursor_example.execute(sql)
mycursor_example.close()
