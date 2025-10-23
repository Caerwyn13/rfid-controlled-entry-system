"""
Entry point of the program
Opens up a login window
"""

import tkinter as tk
from tkinter import messagebox

import requests

import mainwindow


# Create root window
root = tk.Tk()
root.title("Log in | Carpal Inc.")

window_width = 300
window_height = 200
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

centre_x = int(screen_width/2 - window_width/2)
centre_y = int(screen_height/2 - window_height/2)

root.geometry(f"{window_width}x{window_height}+{centre_x}+{centre_y}")
root.resizable(True, True)
root.iconbitmap("assets/main_window.ico")

# Validate login input
def validate_login():
    userid = username_entry.get()
    password = password_entry.get()

    # Send the username and password to the Flask server for validation
    url = 'http://127.0.0.1:5000/auth/validate_credentials'  #! May need to be updated
    data = {'username': userid, 'password': password}

    try:
        response = requests.post(url, data=data)

        if response.status_code == 200:  # Success (Validation passed)
            root.destroy()  # Close the login window
            mainwindow.main()  # Call the main window function
        else:  # Failed (Validation failed)
            error_message = response.json().get("message", "Unknown error")
            messagebox.showerror("Login Failed", error_message)
    
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error connecting to server: {e}")


# Username entry
username_label = tk.Label(root, text="Username: ")
username_label.pack()

username_entry = tk.Entry(root)
username_entry.pack()


# Password entry
password_label = tk.Label(root, text="Password: ")
password_label.pack()

password_entry = tk.Entry(root, show="*")
password_entry.pack()


# Login button
login_button = tk.Button(root, text="Login", command=validate_login)
login_button.pack()


root.mainloop()
