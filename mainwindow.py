import threading
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)

from flask import current_app
import flaskr
import requests

window_scale = 3.5


class App():
    def __init__(self, username):
        self.root = tk.Tk()
        self.window_width = int(300 * window_scale)
        self.window_height = int(200 * window_scale)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.username = username

        centre_x = int(self.screen_width/2 - self.window_width/2)
        centre_y = int(self.screen_height/2 - self.window_height/2)

        # Set up window
        self.root.title("Data Analyser | Carpal Inc.")
        self.root.geometry(f"{self.window_width}x{self.window_height}+{centre_x}+{centre_y}")
        self.root.resizable(True, True)
        self.root.iconbitmap("assets/main_window.ico")

        # Set up tab control
        self.tab_control = ttk.Notebook(self.root)

        self.home_tab = ttk.Frame(self.tab_control)
        self.querying_tab = ttk.Frame(self.tab_control)
        self.database_tab = ttk.Frame(self.tab_control)
        self.settings_tab = ttk.Frame(self.tab_control)
        self.account_tab = ttk.Frame(self.tab_control)
        self.functions_tab = ttk.Frame(self.tab_control)
        self.view_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.home_tab, text = "Home")
        self.tab_control.add(self.querying_tab, text = "Querying")
        self.tab_control.add(self.database_tab, text = "Database")
        self.tab_control.add(self.settings_tab, text = "Settings")
        self.tab_control.add(self.account_tab, text = "Account")

        #TODO: Align these tabs to the right
        self.tab_control.add(self.functions_tab, text = "Functions")
        self.tab_control.add(self.view_tab, text = "View")
        self.tab_control.grid(row=0, column=0, columnspan=1)

        self.greet()
        self.setup_buttons()

        self.style = ttk.Style()
        self.style.configure("TNotebook.Tab", padding=(20, 5))

        self.plot_test()
        self.query_tab()


    def greet(self):
        try:
            response = requests.get(f"http://127.0.0.1:5000/user/get_name/{self.username}")
            response.raise_for_status()
            data = response.json()
            name = data.get("fname").title()
            messagebox.showinfo("Welcome!", f"Welcome {name}!")
        except requests.exceptions.HTTPError as e:
            messagebox.showerror("Error!", f"Name for user {self.username} not found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def setup_buttons(self):
        # Logout button
        #TODO: Style this button to look not so out-of-place in tab control
        self.logout_icon = tk.PhotoImage(file="assets/logout.png").subsample(15, 15)

        self.logout_button = tk.Button(
            self.root,
            image=self.logout_icon,
            text="Log Out",
            compound=tk.LEFT,
            command=self.root.destroy
        ).grid(row=0, column=0, sticky="e", padx=0, pady=0)


    def plot_test(self):
        graph_plot = flaskr.plotting.BarchartPlot()
        canvas = FigureCanvasTkAgg(graph_plot, master=self.home_tab)  
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0)

        toolbar = NavigationToolbar2Tk(canvas, self.home_tab, pack_toolbar=False)   # False as 'grid' is used instead of 'pack'
        toolbar.update()
        canvas.get_tk_widget().grid(row=0, column=1)


    def query_tab(self):
        # Input for SQL queries
        sqlLabel = tk.Label(self.querying_tab, text = "Enter your SQL query:")
        self.sqlQuery = tk.Entry(self.querying_tab, relief="raised")
        sqlSendBtn = tk.Button(self.querying_tab, text = "Send Request", command=self.send_query)

        sqlLabel.grid(row=0, column=0, padx=15, pady=15)
        self.sqlQuery.grid(row=0, column=1, padx=15, pady=15)
        sqlSendBtn.grid(row=1, column=0, columnspan=2, padx=15, pady=15)

        # Frame for storing query results
        self.query_results_frame = ttk.Frame(self.querying_tab)
        self.query_results_frame.pack(fill="both", expand=True)


    def send_query(self):
        query = self.sqlQuery.get()

        # Create a new thread to execute the query
        query_thread = threading.Thread(target=self.execute_query_in_background, args=(query,))
        query_thread.start()

    def execute_query_in_background(self, query):
        try:
            # Ensure Flask's app context is available when making the query
            with current_app.app_context():
                results = flaskr.querying.execute_sql_query(query)

            # After the query is done, update the Tkinter UI (main thread)
            self.update_query_results(results)
        except Exception as e:
            self.show_error_message(str(e))

    def update_query_results(self, results):
        # Run this in the Tkinter main thread
        for widget in self.query_results_frame.winfo_children():
            widget.destroy()  # Remove results from previous query

        self.results_tree = ttk.Treeview(self.query_results_frame, show="headings")
        self.results_tree.pack(fill="both", expand=True)

        columns = [f"Column {i + 1}" for i in range(len(results[0]))]
        self.results_tree["columns"] = columns

        for c in columns:
            self.results_tree.heading(c, text=c)
            self.results_tree.column(c, anchor="center")

        for r in results:
            self.results_tree.insert("", "end", values=r)

    def show_error_message(self, message):
        # Show error message in Tkinter main thread
        messagebox.showerror("Error", message)
            

    def run(self):
        self.root.mainloop()



def main(username):
    tkWindow = App(username)
    tkWindow.run()
