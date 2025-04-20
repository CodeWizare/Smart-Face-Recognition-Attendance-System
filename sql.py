import sqlite3

try:
    sqlite_version = sqlite3.sqlite_version
    print(f"SQLite is installed. Version: {sqlite_version}")
except Exception as e:
    print(f"SQLite not installed or error occurred: {e}")
