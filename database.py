import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def init_db():
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    
    # User table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Market data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            market_name TEXT NOT NULL,
            open_price REAL,
            close_price REAL,
            high REAL,
            low REAL,
            volume INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def add_market_data(data):
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO market_data (date, market_name, open_price, close_price, high, low, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

# Create the SQLite database engine
DATABASE_URL = "sqlite:///market_trends.db"

engine = create_engine(DATABASE_URL, echo=True)  # Set echo=True for debugging SQL queries

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for getting a database session
def get_db():
    """
    Dependency to provide a database session.
    Usage in other modules to ensure proper session handling.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
