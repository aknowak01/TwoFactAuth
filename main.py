import smtplib
from sqlite3 import Error
from time import sleep
from tkinter import *
import sqlite3 as sql
import hashlib
from tkinter.ttk import Treeview
from tkintertable import TableCanvas


class gmail:
    mail_password = "wbmhvqzujspoprnv"
    mail_user = "Fason199@gmail.com"
    key = ""


def code_hash(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


def hash_verify(password, hashed_password):
    if hashed_password == code_hash(password):
        return True
    else:
        return False


def user_register_verification(username):
    cur = conn.cursor()
    cur.execute("SELECT name, password FROM Users WHERE "
                "name = ?", [username])
    data = cur.fetchone()
    if data is None:
        return False
    else:
        return True


def user_login_verification(username, password, verification_key):
    cur = conn.cursor()
    cur.execute("SELECT Users.name, Users.password, Users.verification_key FROM Users WHERE  Users.name = ?",
                [username])
    data = cur.fetchone()
    if hash_verify(password, data[1]) and verification_key == data[2]:
        if data is not None:
            return True
        else:
            return False
    else:
        return False


def create_conection():
    try:
        conn = sql.connect('identifier.sqlite')
        return conn
    except Error:
        print(Error)


def insert_data(name, email, password, verification_key):
    cur = conn.cursor()
    hashed_password = code_hash(password)
    cur.execute("INSERT INTO Users VALUES (?, ?, ?, ?)", (name, email, hashed_password, verification_key))
    conn.commit()


def select_data():
    cur = conn.cursor()
    cur.execute("SELECT name, password, verification_key FROM Users")
    rows = cur.fetchall()
    return rows


def key_generator():
    import random
    import string
    result_str = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
    return result_str


def send_verification_email(username, password, verification_key):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail.mail_user, gmail.mail_password)
        subject = "Verification key"
        body = "Your verification key is: " + verification_key
        message = f'Subject: {subject}\n\n{body}'
        server.sendmail(gmail.mail_user, username, message)
        return True
    except:
        return False


class StartWindow(Tk):
    def __init__(self):
        super().__init__()

        self.button1 = Button(self, text="Sign in", command=self.go_to_window2)
        self.button1.pack()

        self.button2 = Button(self, text="Sign up", command=self.go_to_window3)
        self.button2.pack()

    def go_to_window2(self):
        self.destroy()
        loginwindow = LoginWindow()

    def go_to_window3(self):
        self.destroy()
        registerwindow = RegisterWindow()


class LoginWindow(Tk):
    def __init__(self):
        super().__init__()
        self.label = Label(self, text="This is Window 2")
        self.label = Label(self, text="Name:")
        self.label.grid(row=0, column=0)
        self.username_entry = Entry(self)
        self.username_entry.grid(row=0, column=1)

        self.label = Label(self, text="Password:")
        self.label.grid(row=1, column=0)
        self.password_entry = Entry(self, show="*")
        self.password_entry.grid(row=1, column=1)

        self.label = Label(self, text="Verification key:")
        self.label.grid(row=2, column=0)
        self.verification_key_entry = Entry(self)
        self.verification_key_entry.grid(row=2, column=1)

        self.login_button = Button(self, text="Log in", command=self.on_login)
        self.login_button.grid(row=4, column=1)

        self.label = Label(self)
        self.label.grid(row=4, column=0)

    def on_login(self):

        if self.username_entry == "" or self.password_entry == "" or self.verification_key_entry == "":
            self.label.config(text="Please fill in all fields.")
        else:
            if user_login_verification(self.username_entry.get(), self.password_entry.get(),
                                       self.verification_key_entry.get()):
                self.label.config(text="Login successful.")
                self.destroy()
                mainwindow = MainWindow()

            else:
                self.label.config(text="Login failed.")


class RegisterWindow(Tk):
    def __init__(self):
        super().__init__()
        self.label = Label(self, text="Login:")
        self.label.grid(row=0, column=0)
        self.username_entry = Entry(self)
        self.username_entry.grid(row=0, column=1)

        self.label = Label(self, text="Password:")
        self.label.grid(row=1, column=0)
        self.password_entry = Entry(self, show="*")
        self.password_entry.grid(row=1, column=1)

        self.label = Label(self, text="Email")
        self.label.grid(row=2, column=0)
        self.email_entry = Entry(self)
        self.email_entry.grid(row=2, column=1)

        self.login_button = Button(self, text="Log in", command=self.on_register)
        self.login_button.grid(row=4, column=1)

        self.label = Label(self)
        self.label.grid(row=4, column=0)

    def on_register(self):
        gmail.key = key_generator()
        if self.username_entry == "" or self.password_entry == "" or self.email_entry == "":
            self.label.config(text="Please fill in all fields.")
        else:
            if not user_register_verification(self.username_entry.get()):
                if send_verification_email(self.email_entry.get(), gmail.mail_password, gmail.key):
                    self.label.config(text="Verification key sent to your email.")
                    insert_data(self.username_entry.get(), self.email_entry.get(), self.password_entry.get(), gmail.key)
                    sleep(2)
                    self.label.config(text="Registered successful.")
                    sleep(2)
                    self.destroy()
                    mainwindow = MainWindow()
                else:
                    self.label.config(text="Error email not sent.")

            else:
                self.label.config(text="Registration failed.")


class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.listbox = Listbox(self, width=100, height=10)
        self.listbox.pack()

        show_table_button = Button(self, text="Show Table", command=self.show_table)
        show_table_button.pack()

    def show_table(self):
        con = create_conection()
        cur = con.cursor()

        # Fetch the data
        cur.execute("SELECT name, password, verification_key FROM Users")
        data = cur.fetchall()
        self.listbox.insert(END, "Name" + " " * 10 + "Password" + " " * 10 + "Verification key")
        for row in data:
            self.listbox.insert(END, row[0] + " " * 10 + row[1] + " " * 10 + row[2])

        # Close the connection
        con.close()


startwindow = StartWindow()
conn = create_conection()
startwindow.mainloop()
