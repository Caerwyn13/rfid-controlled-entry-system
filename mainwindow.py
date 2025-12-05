import threading
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import flaskr
import requests

window_scale = 3.5


class App():
    def __init__(self, username, flask_app):
        self.root = tk.Tk()
        self.window_width = int(300 * window_scale)
        self.window_height = int(200 * window_scale)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.username = username
        self.app = flask_app

        centre_x = int(self.screen_width / 2 - self.window_width / 2)
        centre_y = int(self.screen_height / 2 - self.window_height / 2)

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

        self.tab_control.add(self.home_tab, text="Home")
        self.tab_control.add(self.querying_tab, text="Querying")
        self.tab_control.add(self.database_tab, text="Database")
        self.tab_control.add(self.settings_tab, text="Settings")
        self.tab_control.add(self.account_tab, text="Account")
        self.tab_control.add(self.functions_tab, text="Functions")
        self.tab_control.add(self.view_tab, text="View")

        # Make tab alignments
        self.tab_control.grid(row=0, column=0, columnspan=1, padx=10, pady=10)

        self.greet()
        self.setup_buttons()

        self.style = ttk.Style()
        self.style.configure("TNotebook.Tab", padding=(20, 5), font=("Helvetica", 12, "bold"), background="#e0e0e0", width=20)

        # Test plot on home tab
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
        self.logout_icon = tk.PhotoImage(file="assets/logout.png").subsample(15, 15)

        self.logout_button = tk.Button(
            self.root,
            image=self.logout_icon,
            text="Log Out",
            compound=tk.LEFT,
            command=self.root.destroy,
            bg="#ff4d4d",  # Light red color
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief="raised"
        )
        self.logout_button.grid(row=0, column=0, sticky="e", padx=10, pady=10)

    def plot_test(self):
        graph_plot = flaskr.plotting.BarchartPlot(self.app)
        canvas = FigureCanvasTkAgg(graph_plot, master=self.home_tab)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=15, pady=15)

        toolbar = NavigationToolbar2Tk(canvas, self.home_tab, pack_toolbar=False)
        toolbar.update()
        canvas.get_tk_widget().grid(row=0, column=1, padx=15, pady=15)

    def send_query(self):
        query = self.sqlQuery.get()

        # Create a new thread to execute query
        query_thread = threading.Thread(target=self.execute_query_in_background, args=(query,))
        query_thread.start()

    def execute_query_in_background(self, query):
        try:
            # Ensure Flask's app context is available when making the query
            with self.app.app_context():
                results = flaskr.querying.execute_sql_query(query, self.username)

            # After the query is done, update the table
            self.update_query_results(results)
        except Exception as e:
            # Show error message from the main thread
            self.show_error_message(str(e))

    def query_tab(self):
        # Input for SQL queries
        sql_label = tk.Label(self.querying_tab, text="Enter your SQL query:", font=("Helvetica", 12))
        sql_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.sqlQuery = tk.Entry(self.querying_tab, relief="raised", font=("Helvetica", 12))
        self.sqlQuery.grid(row=0, column=1, padx=15, pady=15)

        sql_send_btn = tk.Button(self.querying_tab, text="Send Request", command=self.send_query, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white")
        sql_send_btn.grid(row=1, column=0, columnspan=2, padx=15, pady=15)

        # Frame for storing query results
        self.query_results_frame = ttk.Frame(self.querying_tab)
        self.query_results_frame.grid(row=2, column=0, columnspan=10, padx=15, pady=15)

        # Create a Canvas widget for scrollable content
        self.query_canvas = tk.Canvas(self.query_results_frame)
        self.query_canvas.grid(row=0, column=0, sticky="nsew")

        # Create scrollbars for the canvas
        self.vertical_scrollbar = tk.Scrollbar(self.query_results_frame, orient="vertical", command=self.query_canvas.yview)
        self.vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        self.query_canvas.configure(yscrollcommand=self.vertical_scrollbar.set)

        self.horizontal_scrollbar = tk.Scrollbar(self.query_results_frame, orient="horizontal", command=self.query_canvas.xview)
        self.horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        self.query_canvas.configure(xscrollcommand=self.horizontal_scrollbar.set)

        # Create a frame inside the canvas to hold the Treeview
        self.query_frame = ttk.Frame(self.query_canvas)
        self.query_canvas.create_window((0, 0), window=self.query_frame, anchor="nw")

        # Configure the scrolling region to match the content size
        self.query_frame.bind("<Configure>", lambda e: self.query_canvas.configure(scrollregion=self.query_canvas.bbox("all")))

    def update_query_results(self, results):
        # Ensure the UI updates are done in the main thread
        self.querying_tab.after(0, self._update_query_results, results)

    def _update_query_results(self, results):
        # Clear previous results in the frame
        for widget in self.query_frame.winfo_children():
            widget.destroy()

        if isinstance(results, str):  # If it's a string, it's non-SELECT query result (e.g., "X rows affected")
            label = tk.Label(self.query_frame, text=results, font=("Helvetica", 12))
            label.grid(row=0, column=0, padx=15, pady=10)
        else:
            self.results_tree = ttk.Treeview(self.query_frame, show="headings", height=5)
            self.results_tree.grid(row=0, column=0, sticky="nsew")

            # Define the column headers based on the number of columns in the result
            columns = [f"Column {i + 1}" for i in range(len(results[0]))]
            self.results_tree["columns"] = columns

            for c in columns:
                self.results_tree.heading(c, text=c)
                self.results_tree.column(c, anchor="center")

            # Insert rows into the Treeview
            for r in results:
                self.results_tree.insert("", "end", values=r)

            # Update the canvas scrollregion to fit the content size
            self.query_canvas.update_idletasks()
            self.query_canvas.configure(scrollregion=self.query_canvas.bbox("all"))


    def show_error_message(self, message):
        # Ensure the error message box is shown in the main thread
        self.querying_tab.after(0, lambda: messagebox.showerror("Error", message))

    def run(self):
        self.root.mainloop()


def main(username, flask_app):
    tkWindow = App(username, flask_app)
    tkWindow.run()
