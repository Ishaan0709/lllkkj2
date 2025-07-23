import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('medmentor.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        college TEXT,
        specialization TEXT,
        simulations_completed INTEGER,
        total_simulations INTEGER,
        best_performance TEXT,
        surgeries_this_week INTEGER,
        avg_score REAL,
        feedback TEXT,
        weak_areas TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Chat history table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        message TEXT,
        reply TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )''')
    
    # Insert sample users
    users = [
        ('ishaan', 'Ishaan', 'AIIMS Delhi', 'Cardiothoracic Surgery', 7, 10, 
         'Heart Bypass - 4.8 ⭐', 3, 4.4, 'Needs to revise tool usage in neuro', 'artery clamping'),
        
        ('jyotika', 'Jyotika', 'CMC Vellore', 'Neurosurgery', 5, 8, 
         'Neuro - 4.6 ⭐', 5, 4.2, 'Impressive handling of neurosurgery steps', 'suture stitching')
    ]
    
    c.executemany('''INSERT OR IGNORE INTO users VALUES 
        (?,?,?,?,?,?,?,?,?,?,?, datetime('now'))''', users)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")