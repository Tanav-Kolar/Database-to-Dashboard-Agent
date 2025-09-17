import sqlite3

try:
    # Connect to the database file
    conn = sqlite3.connect("Chinook_Sqlite.sqlite")
    print("Successfully connected to the Chinook database!")
    
    # You can now create a cursor and run queries
    cursor = conn.cursor()
    cursor.execute("SELECT Name FROM Artist LIMIT 5;")
    artists = cursor.fetchall()
    print("First 5 artists:", artists)

except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    if conn:
        conn.close()
        