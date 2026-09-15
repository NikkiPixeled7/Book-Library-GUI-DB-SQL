import sqlite3
import csv
import tkinter as tk
from tkinter import ttk

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

def show_all_books():

    loading_window = tk.Toplevel(window)
    loading_window.title("Loading")
    loading_window.geometry("300x120")
    loading_window.configure(bg="#5884B3")

    loading_label = tk.Label(
        loading_window,
        text="Loading books...\nThis may take up to 10 seconds.",
        font=("Arial", 12),
        bg="#5884B3",
        fg="white"
    )
    loading_label.pack(expand=True)

    loading_window.transient(window)
    loading_window.grab_set()

    window.update()

    for book in book_list.get_children():
        book_list.delete(book)

    cursor.execute("SELECT book_id, title, authors, average_rating FROM books")
    books = cursor.fetchall()

    for book in books:
        if book[3] == 0.0:
            book = (book[0], book[1], book[2], "")

        book_list.insert("", tk.END, values=book)

    loading_window.destroy()

def search_books():

    for book in book_list.get_children():
        book_list.delete(book)

    search_text = search_box.get()

    cursor.execute("""
        SELECT book_id, title, authors, average_rating
        FROM books
        WHERE title LIKE ? OR authors LIKE ?
    """, (f"%{search_text}%", f"%{search_text}%"))

    books = cursor.fetchall()

    for book in books:
        if book[3] == 0.0:
            book = (book[0], book[1], book[2], "")

        book_list.insert("", tk.END, values=book)

def show_book_details(event):
    selected = book_list.selection()

    if not selected:
        return

    book = book_list.item(selected[0], "values")

    book_id = book[0]

    cursor.execute("""
    SELECT title, subtitle, authors, publisher, published_date, description, page_count, categories, average_rating, ratings_count, language, isbn_13, isbn_10, list_price, currency
    FROM books
    WHERE book_id = ?
    """, (book_id,))

    details = cursor.fetchone()

    details_text = (
        "Title: " + str(details[0]) + "\n"
        "Subtitle: " + str(details[1]) + "\n"
        "Author: " + str(details[2]) + "\n"
        "Publisher: " + str(details[3]) + "\n"
        "Published: " + str(details[4]) + "\n"
        "Pages: " + str(details[5]) + "\n"
        "Category: " + str(details[6]) + "\n"
        "Rating: " + str(details[7]) + "\n"
        "Ratings: " + str(details[8]) + "\n"
        "Language: " + str(details[9]) + "\n"
        "ISBN-13: " + str(details[10]) + "\n"
        "ISBN-10: " + str(details[11]) + "\n"
        "Price: " + str(details[12]) + " " + str(details[13])
    )

    details_label.config(text=details_text)

    book_list.bind("<<TreeviewSelect>>", show_book_details)


window = tk.Tk()
window.configure(bg="#5884B3")

window.title("Library Database")

window.geometry("800x600")

title_label = tk.Label(window, text="Library Database", font=("Arial", 24), bg="#5884B3")
title_label.pack(pady=20)

search_frame = tk.Frame(window, bg="#5884B3")
search_frame.pack(pady=10)

search_label = tk.Label(search_frame, text="Search:", bg="#5884B3")
search_label.pack(side="left", padx=5)

search_box = tk.Entry(search_frame, bg="#AFB1B3", width=40)
search_box.pack(side="left", padx=5)

search_button = tk.Button(search_frame, text="Search", command=search_books)
search_button.pack(side="left", padx=5)

button_frame = tk.Frame(window, bg="#5884B3")
button_frame.pack(pady=10)

show_all_button = tk.Button(button_frame, text="Import DB", command=show_all_books)
show_all_button.pack(side="left", padx=5)

add_button = tk.Button(button_frame, text="Add Book")
add_button.pack(side="left", padx=5)

delete_button = tk.Button(button_frame, text="Delete Book")
delete_button.pack(side="left", padx=5)

sort_options = ["Title", "Author", "Rating", "Price"]

sort_dropdown = ttk.Combobox(window, values=sort_options, state="readonly")
sort_dropdown.set("Title")
sort_dropdown.pack(pady=5)

book_list = ttk.Treeview(window, columns=("ID", "Title", "Author", "Rating"), show="headings")

book_list.heading("ID", text="ID")
book_list.heading("Title", text="Title")
book_list.heading("Author", text="Author")
book_list.heading("Rating", text="Rating")

book_list.pack(fill="both", expand=True, padx=20, pady=20)

details_frame = tk.Frame(window, bg="#5884B3")
details_frame.pack(pady=10)

details_label = tk.Label(details_frame, text="Select a book to see more details.", bg="#5884B3", font=("Arial", 12))
details_label.pack()

exit_button = tk.Button(window, text="Exit", command=window.destroy)
exit_button.pack(pady=10)

window.mainloop()
