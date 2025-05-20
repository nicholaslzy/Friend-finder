from cs50 import SQL

# Connect to the database
db = SQL("sqlite:///users.db")

# Create users table for authentication
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
)
""")

# Create users_info table for profile information
db.execute("""
CREATE TABLE IF NOT EXISTS users_info (
    user_id INTEGER,
    name TEXT,
    age INTEGER,
    gender TEXT,
    school TEXT,
    course TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# Create friend_requests table to track pending/accepted/declined requests
db.execute("""
CREATE TABLE IF NOT EXISTS friend_requests (
    sender_id INTEGER,
    receiver_id INTEGER,
    status TEXT,
    FOREIGN KEY(sender_id) REFERENCES users(id),
    FOREIGN KEY(receiver_id) REFERENCES users(id)
)
""")

# Create relationships table to store established friendships
db.execute("""
CREATE TABLE IF NOT EXISTS relationships (
    user_id INTEGER,
    friend_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(friend_id) REFERENCES users(id)
)
""")

print("Database initialized successfully!")