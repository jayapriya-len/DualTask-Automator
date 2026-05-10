# ==========================
# DualTask Automator Project
# ==========================

import tkinter as tk
from tkinter import ttk, messagebox
import pymysql as db
from PIL import Image, ImageTk
from datetime import datetime
import pywhatkit as pk
import random
import threading
import os

# -----------------------------
# DATABASE CONNECTION FUNCTION
# -----------------------------
def connect_db():
    try:
        conn = db.connect(host="localhost", user="root", password="crimepartner", database="dualtask_db")
        return conn
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to connect to database:\n{e}")
        return None


# -----------------------------
# SAVE DATA TO DATABASE
# -----------------------------
def save_to_db(name, phone, msg, time):
    conn = connect_db()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        msg_id = random.randint(1000, 9999)
        cursor.execute("INSERT INTO messages (id, name, phone, message, time) VALUES (%s, %s, %s, %s, %s)",
                       (msg_id, name, phone, msg, time))
        conn.commit()
        conn.close()
        log_to_file(name, phone, msg, time, msg_id)
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to save data:\n{e}")


# -----------------------------
# LOG TO TEXT FILE
# -----------------------------
def log_to_file(name, phone, msg, time, msg_id):
    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")

        with open("logs/messages_log.txt", "a") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{now}] ID: {msg_id} | Name: {name} | Phone: {phone} | Time: {time} | Message: {msg}\n")
    except Exception as e:
        print(f"Log error: {e}")


# -----------------------------
# SEND MESSAGE FUNCTION
# -----------------------------
def send_message():
    name = name_var.get().strip()
    phone = phone_var.get().strip()
    msg = msg_var.get().strip()
    time = time_var.get().strip()

    if not (name and phone and msg and time):
        messagebox.showwarning("Warning", "All fields are required!")
        return

    try:
        hr, min_ = map(int, time.split(":"))

        # Schedule WhatsApp message using pywhatkit
        pk.sendwhatmsg(phone, msg, hr, min_)

        # Save details to database
        save_to_db(name, phone, msg, time)

        messagebox.showinfo("Success", "Message scheduled and saved successfully!")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter time in HH:MM format!")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")


# -----------------------------
# RUN THREAD FUNCTION
# -----------------------------
def start_thread():
    t = threading.Thread(target=send_message)
    t.start()


# -----------------------------
# CLEAR ALL INPUT FIELDS
# -----------------------------
def clear_fields():
    name_var.set("")
    phone_var.set("")
    msg_var.set("")
    time_var.set("")


# -----------------------------
# CREATE DATABASE TABLE IF NOT EXISTS
# -----------------------------
def setup_database():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT PRIMARY KEY,
                name VARCHAR(100),
                phone VARCHAR(20),
                message TEXT,
                time VARCHAR(10)
            )
        """)
        conn.commit()
        conn.close()


# -----------------------------
# MAIN WINDOW SETUP
# -----------------------------
root = tk.Tk()
root.title("DualTask Automator - WhatsApp Scheduler")
root.geometry("600x600")
root.resizable(False, False)
root.configure(bg="#1a1a2e")

# -----------------------------
# TITLE LABEL
# -----------------------------
title_label = tk.Label(root, text="📱 DualTask Automator", font=("Helvetica", 20, "bold"), bg="#1a1a2e", fg="#00adb5")
title_label.pack(pady=20)

# -----------------------------
# LOGO / IMAGE
# -----------------------------
try:
    img = Image.open("logo.png")
    img = img.resize((100, 100))
    photo = ImageTk.PhotoImage(img)
    tk.Label(root, image=photo, bg="#1a1a2e").pack()
except:
    tk.Label(root, text="[No Logo Found]", bg="#1a1a2e", fg="gray").pack(pady=10)

# -----------------------------
# FORM FRAME
# -----------------------------
form_frame = tk.Frame(root, bg="#1a1a2e")
form_frame.pack(pady=10)

label_style = {"bg": "#1a1a2e", "fg": "white", "font": ("Arial", 12, "bold")}

# Name
tk.Label(form_frame, text="Full Name", **label_style).grid(row=0, column=0, padx=10, pady=10, sticky="w")
name_var = tk.StringVar()
ttk.Entry(form_frame, textvariable=name_var, width=35).grid(row=0, column=1, padx=10)

# Phone
tk.Label(form_frame, text="Phone Number (+91...)", **label_style).grid(row=1, column=0, padx=10, pady=10, sticky="w")
phone_var = tk.StringVar()
ttk.Entry(form_frame, textvariable=phone_var, width=35).grid(row=1, column=1, padx=10)

# Message
tk.Label(form_frame, text="Message", **label_style).grid(row=2, column=0, padx=10, pady=10, sticky="w")
msg_var = tk.StringVar()
ttk.Entry(form_frame, textvariable=msg_var, width=35).grid(row=2, column=1, padx=10)

# Time
tk.Label(form_frame, text="Time (HH:MM)", **label_style).grid(row=3, column=0, padx=10, pady=10, sticky="w")
time_var = tk.StringVar()
ttk.Entry(form_frame, textvariable=time_var, width=35).grid(row=3, column=1, padx=10)

# -----------------------------
# BUTTON FRAME
# -----------------------------
button_frame = tk.Frame(root, bg="#1a1a2e")
button_frame.pack(pady=20)

ttk.Button(button_frame, text="Send Message", command=start_thread).grid(row=0, column=0, padx=15)
ttk.Button(button_frame, text="Clear", command=clear_fields).grid(row=0, column=1, padx=15)

# -----------------------------
# DATE/TIME DISPLAY
# -----------------------------
time_label = tk.Label(root, text="", bg="#1a1a2e", fg="#00ffab", font=("Consolas", 12))
time_label.pack(pady=10)


def update_clock():
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    time_label.config(text=f"Current Time: {now}")
    root.after(1000, update_clock)


update_clock()
setup_database()

# -----------------------------
# MAINLOOP
# -----------------------------
root.mainloop()