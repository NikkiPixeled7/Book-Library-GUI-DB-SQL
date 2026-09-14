import sqlite3
import csv
import tkinter as tk

connection = sqlite3.connect("library.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY,
    title TEXT,
    subtitle TEXT,
    authors TEXT,
    publisher TEXT,
    published_date TEXT,
    description TEXT,
    page_count INTEGER,
    categories TEXT,
    average_rating REAL,
    ratings_count INTEGER,
    language TEXT,
    isbn_13 TEXT,
    isbn_10 TEXT,
    list_price REAL,
    currency TEXT
)
""")

with open("google_books_dataset.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        cursor.execute("""
        INSERT INTO books (title, subtitle, authors, publisher, published_date, description, page_count, categories, average_rating, ratings_count, language, isbn_13, isbn_10, list_price, currency)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["title"], row["subtitle"], row["authors"], row["publisher"], row["published_date"],
            row["description"], int(float(row["page_count"] or 0)), row["categories"], float(row["average_rating"] or 0),
            int(float(row["ratings_count"] or 0)), row["language"], row["isbn_13"], row["isbn_10"], float(row["list_price"] or 0), row["currency"]
        ))

connection.commit()

cursor.execute("SELECT title FROM books")
books = cursor.fetchall()

window = tk.Tk()
window.title("Library Database")
window.geometry("500x400")

for book in books:
    label = tk.Label(window, text=book[0])
    label.pack()

window.mainloop()

connection.close()

print("database successfully created")


