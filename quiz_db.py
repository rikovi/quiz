# quiz_db.py
import sqlite3

def initialize_db():
    conn = sqlite3.connect('quiz_stats.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            score INTEGER,
            duration REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_statistics(name, address, score, duration):
    conn = sqlite3.connect('quiz_stats.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quiz_statistics (name, address, score, duration)
        VALUES (?, ?, ?, ?)
    ''', (name, address, score, duration))
    conn.commit()
    conn.close()

def fetch_statistics():
    conn = sqlite3.connect('quiz_stats.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, score, duration FROM quiz_statistics')
    stats = cursor.fetchall()
    conn.close()
    return stats
