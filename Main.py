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

cursor.execute("SELECT COUNT(*) FROM books")
book_count = cursor.fetchone()[0]

if book_count == 0:

    with open("google_books_dataset.csv", "r", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:
            cursor.execute("""
            INSERT INTO books (
                title, subtitle, authors, publisher, published_date,
                description, page_count, categories, average_rating,
                ratings_count, language, isbn_13, isbn_10,
                list_price, currency
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["title"],
                row["subtitle"],
                row["authors"],
                row["publisher"],
                row["published_date"],
                row["description"],
                int(float(row["page_count"] or 0)),
                row["categories"],
                float(row["average_rating"] or 0),
                int(float(row["ratings_count"] or 0)),
                row["language"],
                row["isbn_13"],
                row["isbn_10"],
                float(row["list_price"] or 0),
                row["currency"]
            ))

    connection.commit()

def refresh_books():

    for book in book_list.get_children():
        book_list.delete(book)

    cursor.execute("""
        SELECT book_id, title, authors, average_rating
        FROM books
    """)

    books = cursor.fetchall()

    for book in books:

        if book[3] == 0.0:
            book = (book[0], book[1], book[2], "")

        book_list.insert("", tk.END, values=book)

def sort_books(event):
    
    sort_by = sort_dropdown.get()

    if sort_by == "Title":
        cursor.execute("SELECT book_id, title, authors, average_rating FROM books ORDER BY title")
    elif sort_by == "Author":
        cursor.execute("SELECT book_id, title, authors, average_rating FROM books ORDER BY authors")
    elif sort_by == "Rating":
        cursor.execute("SELECT book_id, title, authors, average_rating FROM books ORDER BY average_rating DESC")
    elif sort_by == "Price":
        cursor.execute("SELECT book_id, title, authors, average_rating FROM books ORDER BY list_price")

    books = cursor.fetchall()

    for book in book_list.get_children():
        book_list.delete(book)

    for book in books:
        if book[3] == 0.0:
            book = (book[0], book[1], book[2], "")

        book_list.insert("", tk.END, values=book)

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
        SELECT title, subtitle, authors, publisher, published_date,
               description, page_count, categories, average_rating,
               ratings_count, language, isbn_13, isbn_10,
               list_price, currency
        FROM books
        WHERE book_id = ?
    """, (book_id,))

    details = cursor.fetchone()

    details_text = (
        "Title: " + str(details[0]) + "\n\n"
        "Subtitle: " + str(details[1]) + "\n\n"
        "Author: " + str(details[2]) + "\n\n"
        "Publisher: " + str(details[3]) + "\n\n"
        "Published: " + str(details[4]) + "\n\n"
        "Pages: " + str(details[6]) + "\n\n"
        "Category: " + str(details[7]) + "\n\n"
        "Rating: " + ("" if details[8] == 0.0 else str(details[8])) + "\n\n"
        "Ratings: " + str(details[9]) + "\n\n"
        "Language: " + str(details[10]) + "\n\n"
        "ISBN-13: " + str(details[11]) + "\n\n"
        "ISBN-10: " + str(details[12]) + "\n\n"
        "Price: " + str(details[13]) + " " + str(details[14])
    )

    details_textbox.config(state="normal")
    details_textbox.delete("1.0", tk.END)
    details_textbox.insert(tk.END, details_text)
    details_textbox.config(state="disabled")

    description = str(details[5])

    description_textbox.config(state="normal")
    description_textbox.delete("1.0", tk.END)
    description_textbox.insert(tk.END, description)
    description_textbox.config(state="disabled")

    if len(description) > 700:
        description = description[:700] + "..."

window = tk.Tk()
window.configure(bg="#5884B3")

window.title("Library Database")

window.geometry("900x650")

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

show_all_button = tk.Button(button_frame, text="Show All", command=show_all_books)
show_all_button.pack(side="left", padx=5)

add_button = tk.Button(button_frame, text="Add Book")
add_button.pack(side="left", padx=5)

delete_button = tk.Button(button_frame, text="Delete Book")
delete_button.pack(side="left", padx=5)

button_frame2 = tk.Frame(window, bg="#5884B3")
button_frame2.pack(pady=10)

sort_options = ["Title", "Author", "Rating", "Price"]

sort_dropdown = ttk.Combobox(button_frame2, values=sort_options, state="readonly") # read only because you are able to write in the dropdown box thing
sort_dropdown.set("Title")
sort_dropdown.pack(side="left", pady=5)

refresh_button = tk.Button(button_frame2, text="Refresh", command=refresh_books)
refresh_button.pack(side="left", padx=5)

book_list = ttk.Treeview(window, columns=("ID", "Title", "Author", "Rating"), show="headings")

book_list.heading("ID", text="ID")
book_list.heading("Title", text="Title")
book_list.heading("Author", text="Author")
book_list.heading("Rating", text="Rating")

book_list.pack(fill="both", expand=True, padx=20, pady=20)
book_list.bind("<<TreeviewSelect>>", show_book_details)

details_frame = tk.Frame(window, bg="#5884B3")
details_frame.pack(fill="both", expand=True, padx=20, pady=10)

info_frame = tk.Frame(details_frame, bg="#5884B3")
info_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

info_title = tk.Label(
    info_frame,
    text="Book Details",
    bg="#5884B3",
    font=("Arial", 12, "bold")
)

info_title.pack(anchor="w")


info_content_frame = tk.Frame(info_frame)
info_content_frame.pack(fill="both", expand=True)


info_scrollbar = tk.Scrollbar(
    info_content_frame,
    orient="vertical"
)

info_scrollbar.pack(side="right", fill="y")


details_textbox = tk.Text(
    info_content_frame,
    bg="#AFB1B3",
    font=("Arial", 10),
    wrap="word",
    yscrollcommand=info_scrollbar.set
)

details_textbox.pack(side="left", fill="both", expand=True)

info_scrollbar.config(
    command=details_textbox.yview
)

details_textbox.config(state="disabled")

description_frame = tk.Frame(
    details_frame,
    bg="#5884B3"
)

description_frame.pack(
    side="right",
    fill="both",
    expand=True,
    padx=(10, 0)
)


description_title = tk.Label(
    description_frame,
    text="Description",
    bg="#5884B3",
    font=("Arial", 12, "bold")
)

description_title.pack(anchor="w")


description_content_frame = tk.Frame(description_frame)
description_content_frame.pack(fill="both", expand=True)


description_scrollbar = tk.Scrollbar(
    description_content_frame,
    orient="vertical"
)

description_scrollbar.pack(side="right", fill="y")


description_textbox = tk.Text(
    description_content_frame,
    bg="#AFB1B3",
    font=("Arial", 10),
    wrap="word",
    yscrollcommand=description_scrollbar.set
)

description_textbox.pack(
    side="left",
    fill="both",
    expand=True
)

description_scrollbar.config(
    command=description_textbox.yview
)

description_textbox.config(state="disabled")

exit_button = tk.Button(window, text="Exit", command=window.destroy)
exit_button.pack(pady=10)

window.mainloop()
