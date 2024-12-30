from backend.auth import validate_username, validate_password
import pytest
import sqlite3
from backend.database import add_user, get_user
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///market_data.db"  # Change this to your database
engine = create_engine(DATABASE_URL)


def test_validate_username():
    assert validate_username("user") == True
    assert validate_username("abc") == False

def test_validate_password():
    assert validate_password("pass12") == True
    assert validate_password("123") == False

def test_add_user():
    add_user("testuser", "testpassword")
    conn = sqlite3.connect('market_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username='testuser'")
    user = c.fetchone()
    assert user is not None
    conn.close()