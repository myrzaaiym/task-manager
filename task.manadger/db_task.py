import sqlite3

connection = sqlite3.connect("task_manager.db", check_same_thread=False)

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        date TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
