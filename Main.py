import sqlite3
import csv
import tkinter as tk
from tkinter import ttk, messagebox
import time
from cryptography.fernet import Fernet
import os

connection = sqlite3.connect("library.db")

if os.path.exists("secret.key"):
    with open("secret.key", "rb") as file:
        key = file.read()
else:
    key = Fernet.generate_key()

    with open("secret.key", "wb") as file:
        file.write(key)

cipher = Fernet(key)

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

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

encrypted_username = cipher.encrypt("Username".encode()).decode()
encrypted_password = cipher.encrypt("Password".encode()).decode()

cursor.execute("""
INSERT OR IGNORE INTO users (username, password)
VALUES (?, ?)
""", ("Username", encrypted_password))

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

def center_window(window, width, height):

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def animate_loading(popup, label, count=1):
    if popup.winfo_exists():
        dots = "." * count
        label.config(text=f"Logging in{dots}")

        next_count = 1 if count == 3 else count + 1

        popup.after(500, animate_loading, popup, label, next_count)    

def show_popup(place):
    popup = tk.Toplevel(place)
    center_window(popup, 200, 100)
    popup.title("Loading")

    label = tk.Label(popup, text="Logging in.")
    label.pack(pady=30)

    animate_loading(popup, label)

    def finish_login():
        popup.destroy()
        place.withdraw()
        operate_database(place)

    popup.after(3000, finish_login)

def refresh_books():

    for book in book_list.get_children():
        book_list.delete(book)

    cursor.execute("""
        SELECT book_id, title, authors, average_rating, list_price
        FROM books
    """)

    books = cursor.fetchall()

    for book in books:

        if book[3] == 0.0:
            rating = ""
        else:
            rating = book[3]

        if book[4] == 0.0:
            price = ""
        else:
            price = book[4]

        book = (
            book[0],
            book[1],
            book[2],
            rating,
            price
        )

    book_list.insert("", tk.END, values=book)

def sort_books(event):

    sort_by = sort_dropdown.get()
    sort_direction = sort_order_dropdown.get()

    if sort_direction == "Ascending":
        direction = "ASC"
    else:
        direction = "DESC"

    if sort_by == "Title":
        cursor.execute(
            f"""
            SELECT book_id, title, authors, average_rating, list_price
            FROM books
            ORDER BY
                CASE WHEN title IS NULL OR title = '' THEN 1 ELSE 0 END,
                title {direction}
            """
        )

    elif sort_by == "Author":
        cursor.execute(
            f"""
            SELECT book_id, title, authors, average_rating, list_price
            FROM books
            ORDER BY
                CASE WHEN authors IS NULL OR authors = '' THEN 1 ELSE 0 END,
                authors {direction}
            """
        )

    elif sort_by == "Rating":
        cursor.execute(
            f"""
            SELECT book_id, title, authors, average_rating, list_price
            FROM books
            ORDER BY
                CASE WHEN average_rating IS NULL OR average_rating = 0 THEN 1 ELSE 0 END,
                average_rating {direction}
            """
        )

    elif sort_by == "Price":
        cursor.execute(
            f"""
            SELECT book_id, title, authors, average_rating, list_price
            FROM books
            ORDER BY
                CASE WHEN list_price IS NULL OR list_price = 0 THEN 1 ELSE 0 END,
                list_price {direction}
            """
        )

    elif sort_by == "Book ID":
            cursor.execute(
                f"""
                SELECT book_id, title, authors, average_rating, list_price
                FROM books
                ORDER BY
                    CASE WHEN book_id IS NULL OR book_id = '' THEN 1 ELSE 0 END,
                    book_id {direction}
                """
            )

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
    center_window(loading_window, 300, 120)
    loading_window.configure(bg="#5884B3")

    loading_label = tk.Label(
        loading_window,
        text="Loading books...\nThis may take up to 10 seconds.",
        font=("Times New Roman", 12),
        bg="#5884B3",
        fg="white"
    )
    loading_label.pack(expand=True)

    loading_window.transient(window)
    loading_window.grab_set()

    window.update()

    for book in book_list.get_children():
        book_list.delete(book)

    cursor.execute("SELECT book_id, title, authors, average_rating, list_price FROM books")
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
        SELECT book_id, title, authors, average_rating, list_price
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

def add_book():

    add_window = tk.Toplevel(window)
    add_window.title("Add Book")
    add_window.geometry("500x525")
    center_window(add_window, 500, 525)
    add_window.configure(bg="#5884B3")

    labels = [
        "Title", "Subtitle", "Authors", "Publisher", "Published Date",
        "Description", "Page Count", "Categories", "Average Rating",
        "Ratings Count", "Language", "ISBN-13", "ISBN-10",
        "List Price", "Currency"
    ]

    entries = {}

    for i, label in enumerate(labels):

        tk.Label(
            add_window,
            text=label + ":",
            bg="#5884B3"
        ).grid(
            row=i,
            column=0,
            sticky="e",
            padx=5,
            pady=5
        )

        entry = tk.Entry(
            add_window,
            width=30
        )

        entry.grid(
            row=i,
            column=1,
            padx=5,
            pady=5
        )

        entries[label] = entry


    def save_book():

        title = entries["Title"].get()
        subtitle = entries["Subtitle"].get()
        authors = entries["Authors"].get()
        publisher = entries["Publisher"].get()
        published_date = entries["Published Date"].get()
        description = entries["Description"].get()
        categories = entries["Categories"].get()
        language = entries["Language"].get()
        isbn_13 = entries["ISBN-13"].get()
        isbn_10 = entries["ISBN-10"].get()
        currency = entries["Currency"].get()

        if title == "":
            messagebox.showerror(
                "Error",
                "Title is required."
            )
            return

        try:

            page_count = int(
                entries["Page Count"].get() or 0
            )

            average_rating = float(
                entries["Average Rating"].get() or 0
            )

            ratings_count = int(
                entries["Ratings Count"].get() or 0
            )

            list_price = float(
                entries["List Price"].get() or 0
            )

        except ValueError:

            messagebox.showerror(
                "Error",
                "Pages, rating, ratings count, and price must be numbers."
            )

            return


        cursor.execute("""
            INSERT INTO books (
                title,
                subtitle,
                authors,
                publisher,
                published_date,
                description,
                page_count,
                categories,
                average_rating,
                ratings_count,
                language,
                isbn_13,
                isbn_10,
                list_price,
                currency
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            subtitle,
            authors,
            publisher,
            published_date,
            description,
            page_count,
            categories,
            average_rating,
            ratings_count,
            language,
            isbn_13,
            isbn_10,
            list_price,
            currency
        ))

        connection.commit()

        messagebox.showinfo(
            "Success",
            "Book added successfully!"
        )

        add_window.destroy()

        refresh_books()

    add_submit_button = tk.Button(
        add_window,
        text="Add Book",
        command=save_book
    )

    add_submit_button.grid(
        row=len(labels),
        column=0,
        columnspan=2,
        pady=15
    )

def delete_book():

    selected = book_list.selection()

    if not selected:
        messagebox.showerror("Error", "No book selected..")
        return

    book = book_list.item(selected[0], "values")
    book_id = book[0]
    title = book[1]

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{title}'?")

    if not confirm:
        return

    second_confirm = messagebox.askyesno("Double Confirm", f"Are you really sure you want to delete '{title}'?")

    if not second_confirm:
        return

    third_confirm = messagebox.askyesno("Triple Confirm", "Are you really really sure?")

    if not third_confirm:
        messagebox.showinfo("Popup", "Phew..")
        return

    cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))

    connection.commit()

    messagebox.showinfo(
        "Success", f"Book '{title}' deleted successfully."
    )

    refresh_books()

def developer_add_user(home_window):

    user_window = tk.Toplevel(home_window)
    user_window.title("Add New User")
    user_window.geometry("300x220")
    center_window(user_window, 300, 220)
    user_window.configure(bg="#A158B3")

    tk.Label(
        user_window,
        text="Add New User",
        font=("Times New Roman", 18, "bold"),
        bg="#A158B3"
    ).pack(pady=10)

    tk.Label(
        user_window,
        text="Username:",
        bg="#A158B3"
    ).pack()

    username_entry = tk.Entry(user_window)
    username_entry.pack(pady=5)

    tk.Label(
        user_window,
        text="Password:",
        bg="#A158B3"
    ).pack()

    password_entry = tk.Entry(user_window, show="*")
    password_entry.pack(pady=5)

    def confirm_user():

        username = username_entry.get()
        password = password_entry.get()

        if username == "" or password == "":
            messagebox.showerror(
                "Error",
                "Please enter a username and password."
            )
            return

        encrypted_password = cipher.encrypt(
            password.encode()
        ).decode()

        try:
            cursor.execute("""
                INSERT INTO users (username, password)
                VALUES (?, ?)
            """, (username, encrypted_password))

            connection.commit()

            messagebox.showinfo(
                "Success",
                "New user added successfully."
            )

            user_window.destroy()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Error",
                "That username already exists."
            )

    tk.Button(
        user_window,
        text="Confirm",
        command=confirm_user
    ).pack(pady=12)

def home_screen():

    home_window = tk.Tk()
    home_window.title("HS - Library Database V1.0.7")
    home_window.geometry("450x375")
    center_window(home_window, 450, 375)
    home_window.configure(bg="#5884B3")

    welcome_label = tk.Label(home_window, text="Welcome to the Library Database", font=("Times New Roman", 20, "bold"), bg="#5884B3")
    welcome_label.pack(pady=13)

    instructions_label = tk.Label(home_window, text="Please Log-In Below", font=("Times New Roman", 12, "bold"), bg="#5884B3")
    instructions_label.pack(pady=7)

    username_label = tk.Label(home_window, text="Username:", font=("Times New Roman", 12), bg="#5884B3")
    username_label.pack(pady=5)

    username_entry = tk.Entry(home_window, width=30)
    username_entry.pack(pady=2)

    password_label = tk.Label(home_window, text="Password:", font=("Times New Roman", 12), bg="#5884B3")
    password_label.pack(pady=5)

    password_entry = tk.Entry(home_window, show="*", width=30)
    password_entry.pack(pady=2)

    def operate():

        username = username_entry.get()
        password = password_entry.get()

        if username == "" and password == "":
            messagebox.showerror(
                "Error",
                "Username and Password are required."
            )
            return

        elif username == "":
            messagebox.showerror(
                "Error",
                "Username is required."
            )
            return

        elif password == "":
            messagebox.showerror(
                "Error",
                "Password is required."
            )
            return

        cursor.execute("""
            SELECT username, password
            FROM users
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

        if user is not None:
            stored_username = user[0]
            stored_password = user[1]

            try:
                decrypted_password = cipher.decrypt(
                    stored_password.encode()
                ).decode()

                if password == decrypted_password:
                    welcome_label.config(
                        text="Welcome, " + username + "!"
                    )
                    show_popup(home_window)
                else:
                    messagebox.showerror(
                        "Login Failed",
                        "Incorrect username or password."
                    )

            except Exception:
                messagebox.showerror(
                    "Login Failed",
                    "There was a problem checking the password."
                )

        else:
            messagebox.showerror(
                "Login Failed",
                "Incorrect username or password."
            )

    login_button = tk.Button(
        home_window,
        text="Log In",
        command=operate
    )

    login_button.pack(pady=15)

    developer_add_login = tk.Button(home_window, text="Dev Add Login", font=("Times New Roman", 6), command=lambda: developer_add_user(home_window), bg="#BF77F6")
    developer_add_login.pack(side="bottom", anchor="e")

    home_window.mainloop()

def search_by_id():

    id_window = tk.Toplevel(window)
    id_window.title("Search by ID")
    id_window.geometry("300x150")
    center_window(id_window, 300, 150)
    id_window.configure(bg="#5884B3")

    tk.Label(
        id_window,
        text="Enter Book ID:",
        bg="#5884B3",
        font=("Times New Roman", 12)
    ).pack(pady=10)

    id_entry = tk.Entry(id_window, width=25)
    id_entry.pack()

    def search():

        book_id = id_entry.get()

        if book_id == "":
            messagebox.showerror(
                "Error",
                "Please enter a Book ID."
            )
            return

        try:
            book_id = int(book_id)
        except ValueError:
            messagebox.showerror(
                "Error",
                "Book ID must be a number."
            )
            return

        cursor.execute("""
            SELECT book_id, title, authors, average_rating, list_price
            FROM books
            WHERE book_id = ?
        """, (book_id,))

        book = cursor.fetchone()

        if book is None:
            messagebox.showerror(
                "Error",
                "No book found with that ID."
            )
            return

        # Clear the current list
        for item in book_list.get_children():
            book_list.delete(item)

        # Show the found book
        if book[3] == 0.0:
            rating = ""
        else:
            rating = book[3]

        if book[4] == 0.0:
            price = ""
        else:
            price = book[4]

        book = (
            book[0],
            book[1],
            book[2],
            rating,
            price
        )

        book_list.insert("", tk.END, values=book)

        id_window.destroy()

    tk.Button(
        id_window,
        text="Search",
        command=search
    ).pack(pady=15) 

def operate_database(home_window):
    global window, book_list, search_box, sort_dropdown, sort_order_dropdown, details_textbox, description_textbox

    window = tk.Toplevel(home_window)

    def back_to_homescreen():
        window.destroy()
        home_window.deiconify()

    def settings():
        settings_window = tk.Toplevel(window)
        settings_window.title("Settings")
        settings_window.geometry("300x250")
        center_window(settings_window, 300, 250)
        settings_window.configure(bg="#C7C8CA")

        tk.Label(
            settings_window,
            text="Settings",
            font=("Times New Roman", 20, "bold"),
            bg="#C7C8CA"
        ).pack(pady=10)

        ## settings here buttons and whatnot

        tk.Button(
        settings_window,
        text="Close",
        command=settings_window.destroy
        ).pack(pady=15)

    window.configure(bg="#5884B3")

    window.title("MS - Library Database V1.0.7")

    center_window(window, 900, 650)

    title_frame = tk.Frame(window, bg="#5884B3")
    title_frame.pack(fill="x", pady=5)


    back_button = tk.Button(
        title_frame,
        text="Back",
        command=back_to_homescreen,
        bg="#39B0DF",
        font=("", 12, "bold")
    )
    back_button.pack(side="left", padx=10)

    settings_button = tk.Button(
            title_frame,
            text="Settings",
            command=settings,
            bg="#C7C8CA",
            font=("", 10, "bold")
        )
    settings_button.pack(side="right", padx=10)

    title_label = tk.Label(
        title_frame,
        text="Library Database",
        font=("Times New Roman", 24, "bold"),
        bg="#5884B3"
    )
    title_label.pack(pady=7)

    subtitle_label = tk.Label(window, text="✨ Search, sort, and manage your book collection ✨", font=("Segoe UI", 12, "italic"), bg="#5884B3")
    subtitle_label.pack(pady=0)

    author_label = tk.Label(window, text="Created by Nick.C", font=("Times New Roman", 8), bg="#5884B3")
    author_label.pack(pady=2)

    search_frame = tk.Frame(window, bg="#5884B3")
    search_frame.pack(pady=10)

    search_label = tk.Label(search_frame, text="Search:", bg="#5884B3")
    search_label.pack(side="left", padx=5)

    search_box = tk.Entry(search_frame, bg="#AFB1B3", width=40)
    search_box.pack(side="left", padx=5)

    search_button = tk.Button(search_frame, text="Search", command=search_books)
    search_button.pack(side="left", padx=5)
    window.bind("<Return>", lambda event: search_books())

    button_frame = tk.Frame(window, bg="#5884B3")
    button_frame.pack(pady=10)

    show_all_button = tk.Button(button_frame, text="Show All", command=show_all_books)
    show_all_button.pack(side="left", padx=5)

    add_button = tk.Button(button_frame, text="Add Book", command=add_book)
    add_button.pack(side="left", padx=5)

    delete_button = tk.Button(button_frame, text="Delete Book", command=delete_book, bg="#FF0000")
    delete_button.pack(side="left", padx=5)

    search_id_button = tk.Button(
    button_frame,
    text="Search by ID",
    command=search_by_id
)
    search_id_button.pack(side="left", padx=5)

    button_frame2 = tk.Frame(window, bg="#5884B3")
    button_frame2.pack(pady=10)

    sort_options = ["Title", "Author", "Rating", "Price", "Book ID"]
    sort_order = ["Ascending", "Descending"]

    sort_dropdown = ttk.Combobox(button_frame2, values=sort_options, state="readonly") # read only because you are able to write in the dropdown box thing
    sort_dropdown.set("Title")
    sort_dropdown.pack(side="left", pady=5)
    sort_dropdown.bind("<<ComboboxSelected>>", sort_books)

    sort_order_dropdown = ttk.Combobox(button_frame2, values=sort_order, state="readonly") # read only because you are able to write in the dropdown box thing
    sort_order_dropdown.set("Ascending")
    sort_order_dropdown.pack(side="left", padx=5)
    sort_order_dropdown.bind("<<ComboboxSelected>>", sort_books)

    refresh_button = tk.Button(button_frame2, text="Refresh", command=refresh_books)
    refresh_button.pack(side="left", padx=5)

    book_list = ttk.Treeview(window, columns=("ID", "Title", "Author", "Rating", "Price"), show="headings")

    book_list.heading("ID", text="ID")
    book_list.heading("Title", text="Title")
    book_list.heading("Author", text="Author")
    book_list.heading("Rating", text="Rating")
    book_list.heading("Price", text="price")

    book_list.column("ID", width=50)
    book_list.column("Title", width=300)
    book_list.column("Author", width=200)
    book_list.column("Rating", width=80)
    book_list.column("Price", width=80)

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
    font=("Times New Roman", 12, "bold")
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
    font=("Times New Roman", 10),
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
    font=("Times New Roman", 12, "bold")
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
    font=("Times New Roman", 10),
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

home_screen()
