import sqlite3

connection = sqlite3.connect("user_data.db")
db = connection.cursor()

db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR, password VARCHAR)")

connection.commit()
connection.close()
