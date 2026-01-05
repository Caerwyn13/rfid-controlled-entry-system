import threading
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import requests
import flaskr

window_scale = 3.5


class ResultView:
    """Encapsulates a unique scrollable Treeview for each tab"""

    def __init__(self, parent):
        self.container = ttk.Frame(parent)
        self.container.grid(row=2, column=0, columnspan=10, padx=15, pady=15, sticky="nsew")

        self.canvas = tk.Canvas(self.container)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        v_scroll = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=v_scroll.set)

        h_scroll = tk.Scrollbar(self.container, orient="horizontal", command=self.canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=h_scroll.set)

        self.frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

    def clear(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_results(self, results):
        self.clear()

        if isinstance(results, str):
            tk.Label(self.frame, text=results, font=("Helvetica", 12)).grid(padx=15, pady=10)
            return

        tree = ttk.Treeview(self.frame, show="headings")
        tree.grid(sticky="nsew")

        columns = [f"Column {i+1}" for i in range(len(results[0]))]
        tree["columns"] = columns

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for row in results:
            tree.insert("", "end", values=row)


class App:
    def __init__(self, username, flask_app):
        self.username = username
        self.app = flask_app

        self.root = tk.Tk()
        self.root.title("Data Analyser | Carpal Inc.")
        self.root.geometry(self._center_window())
        self.root.iconbitmap("assets/main_window.ico")

        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.tabs = {
            "Home": ttk.Frame(self.tab_control),
            "Querying": ttk.Frame(self.tab_control),
            "Database": ttk.Frame(self.tab_control),
        }

        for name, tab in self.tabs.items():
            self.tab_control.add(tab, text=name)

        self.result_views = {}

        self._setup_home()
        self._setup_query_tab()
        self._setup_database_tab()
        self._greet()

    def _center_window(self):
        w = int(300 * window_scale)
        h = int(200 * window_scale)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        return f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}"

    def _greet(self):
        try:
            r = requests.get(f"http://127.0.0.1:5000/user/get_name/{self.username}")
            r.raise_for_status()
            messagebox.showinfo("Welcome", f"Welcome {r.json()['fname'].title()}!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- HOME TAB ---------------- #

    def _setup_home(self):
        graph = flaskr.plotting.BarchartPlot(self.app)
        canvas = FigureCanvasTkAgg(graph, master=self.tabs["Home"])
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=15, pady=15)

        toolbar = NavigationToolbar2Tk(canvas, self.tabs["Home"], pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=1, column=0, sticky="ew")

    # ---------------- QUERY TAB ---------------- #

    def _setup_query_tab(self):
        tab = self.tabs["Querying"]

        tk.Label(tab, text="Enter SQL Query:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.query_entry = tk.Entry(tab, font=("Helvetica", 12), width=50)
        self.query_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Button(
            tab,
            text="Run Query",
            command=lambda: self.run_query(self.query_entry.get(), tab),
            bg="#4CAF50",
            fg="white"
        ).grid(row=1, column=0, columnspan=2, pady=10)

        self.result_views[tab] = ResultView(tab)

    # ---------------- DATABASE TAB ---------------- #

    def _setup_database_tab(self):
        tab = self.tabs["Database"]

        self.table_var = tk.StringVar(value="users")
        tables = ["users", "departments", "accesslog"]

        ttk.OptionMenu(tab, self.table_var, tables[0], *tables).grid(row=0, column=0, padx=10)
        ttk.Button(
            tab,
            text="View Table",
            command=lambda: self.run_query(
                f"SELECT * FROM {self.table_var.get()}",
                tab
            )
        ).grid(row=0, column=1, padx=10)

        self.result_views[tab] = ResultView(tab)

    # ---------------- QUERY EXECUTION ---------------- #

    def run_query(self, query, tab):
        threading.Thread(
            target=self._execute_query,
            args=(query, tab),
            daemon=True
        ).start()

    def _execute_query(self, query, tab):
        try:
            with self.app.app_context():
                results = flaskr.querying.execute_sql_query(query, self.username)

            self.root.after(
                0,
                lambda: self.result_views[tab].show_results(results)
            )

        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", str(e))
            )

    def run(self):
        self.root.mainloop()


def main(username, flask_app):
    App(username, flask_app).run()
