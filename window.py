import threading
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

import requests
import flaskr


WINDOW_SCALE = 3.5  # Should this be user configureable?

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_LARGE = ("Segoe UI", 12)
FONT_TITLE = ("Segoe UI", 14, "bold")

# Colours
COLOURS = {
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "secondary": "#64748b",
    "background": "#f8fafc",
    "surface": "#ffffff",
    "border": "#e2e8f0",
    "text": "#1e293b",
    "text_secondary": "#64748b",
    "success": "#10b981",
    "error": "#ef4444",
    "row_even": "#f8fafc",
    "row_odd": "#ffffff",
}


# -------------------------------------------------
# ResultView
# Each tab gets its own scrollable results container
# -------------------------------------------------

class ResultView:
    """
    Wrapper around a scrollable Treeview.
    """

    def __init__(self, parent):
        self.container = ttk.Frame(parent, style="Card.TFrame")
        self.container.grid(
            row=2,
            column=0,
            columnspan=10,
            padx=20,
            pady=20,
            sticky="nsew"
        )

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self.container,
            bg=COLOURS["surface"],
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.v_scroll = ttk.Scrollbar(
            self.container,
            orient="vertical",
            command=self.canvas.yview
        )
        self.v_scroll.grid(row=0, column=1, sticky="ns")

        self.h_scroll = ttk.Scrollbar(
            self.container,
            orient="horizontal",
            command=self.canvas.xview
        )
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )

        self.frame = ttk.Frame(self.canvas, style="Card.TFrame")
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # Resize scroll region when content changes
        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

    def clear(self):
        """Remove previous results."""
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_results(self, results):
        """
        Display query output.
        Accepts either a string (error/info) or a 2D list.
        """
        self.clear()

        # UPDATE queries don't return a list
        if isinstance(results, str):
            ttk.Label(
                self.frame,
                text=results,
                font=FONT_LARGE,
                style="Info.TLabel"
            ).grid(padx=20, pady=30)
            return

        tree = ttk.Treeview(
            self.frame,
            style="Custom.Treeview",
            show="headings"
        )
        tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        if not results:
            results = [["No entries match your query"]]

        columns = [f"Column {i + 1}" for i in range(len(results[0]))]
        tree["columns"] = columns

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="w", minwidth=100, stretch=True)

        for i, row in enumerate(results):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.insert("", "end", values=row, tags=(tag,))

        tree.tag_configure("oddrow", background=COLOURS["row_odd"])
        tree.tag_configure("evenrow", background=COLOURS["row_even"])


# -------------------------
# Main application window
# -------------------------

class App:
    def __init__(self, username, flask_app):
        self.username = username
        self.app = flask_app

        self.root = tk.Tk()
        self.root.title("Data Analyser | Carpal Inc.")
        self.root.geometry(self._center_window())
        self.root.configure(bg=COLOURS["background"])

        try:
            self.root.iconbitmap("assets/main_window.ico")
        except Exception:
            # They can live without an icon
            pass

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.style = ttk.Style()
        self._setup_styles()

        main = ttk.Frame(self.root, style="Main.TFrame")
        main.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        self.tabs = ttk.Notebook(main, style="Custom.TNotebook")
        self.tabs.grid(row=0, column=0, sticky="nsew")

        self.tab_frames = {
            "Home": ttk.Frame(self.tabs, style="Tab.TFrame"),
            "Querying": ttk.Frame(self.tabs, style="Tab.TFrame"),
            "Database": ttk.Frame(self.tabs, style="Tab.TFrame"),
        }

        for name, frame in self.tab_frames.items():
            frame.grid_rowconfigure(2, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            self.tabs.add(frame, text=f"  {name}  ")

        self.result_views = {}

        self._setup_home()
        self._setup_query_tab()
        self._setup_database_tab()
        self._greet_user()

    def _center_window(self):
        w = int(300 * WINDOW_SCALE)
        h = int(200 * WINDOW_SCALE)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        return f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}"

    def _greet_user(self):
        """
        Pull the user's name from the backend.
        Fails if Flask isn't ready yet.
        """
        try:
            r = requests.get(
                f"http://127.0.0.1:5000/user/get_name/{self.username}"
            )
            r.raise_for_status()
            fname = r.json().get("fname", self.username)
            messagebox.showinfo("Welcome", f"Welcome {fname.title()}!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- HOME TAB ---------------- #

    def _setup_home(self):
        tab = self.tab_frames["Home"]

        header = ttk.Frame(tab, style="Header.TFrame")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        ttk.Label(
            header,
            text="Dashboard Overview",
            font=FONT_TITLE,
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Data visualization and analytics",
            font=FONT,
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        graph_frame = ttk.Frame(tab, style="Card.TFrame")
        graph_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        graph = flaskr.plotting.BarchartPlot(self.app)
        canvas = FigureCanvasTkAgg(graph, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        toolbar = NavigationToolbar2Tk(
            canvas,
            graph_frame,
            pack_toolbar=False
        )
        toolbar.update()
        toolbar.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

    # ---------------- QUERY TAB ---------------- #

    def _setup_query_tab(self):
        tab = self.tab_frames["Querying"]

        header = ttk.Frame(tab, style="Header.TFrame")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        ttk.Label(
            header,
            text="SQL Query Console",
            font=FONT_TITLE,
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Execute custom SQL queries against the database",
            font=FONT,
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        input_box = ttk.Frame(tab, style="Card.TFrame")
        input_box.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        input_box.grid_columnconfigure(1, weight=1)

        ttk.Label(
            input_box,
            text="Query:",
            font=FONT_BOLD,
            style="Label.TLabel"
        ).grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.query_entry = ttk.Entry(
            input_box,
            style="Custom.TEntry",
            font=FONT
        )
        self.query_entry.grid(
            row=0,
            column=1,
            padx=(5, 15),
            pady=15,
            sticky="ew"
        )

        ttk.Button(
            input_box,
            text="▶ Run Query",
            style="Primary.TButton",
            command=lambda: self.run_query(
                self.query_entry.get(),
                tab
            )
        ).grid(row=0, column=2, padx=(0, 15), pady=15)

        self.result_views[tab] = ResultView(tab)

    # ---------------- DATABASE TAB ---------------- #

    def _setup_database_tab(self):
        tab = self.tab_frames["Database"]

        header = ttk.Frame(tab, style="Header.TFrame")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        ttk.Label(
            header,
            text="Database Explorer",
            font=FONT_TITLE,
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Browse and view database tables",
            font=FONT,
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        select = ttk.Frame(tab, style="Card.TFrame")
        select.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        ttk.Label(
            select,
            text="Select Table:",
            font=FONT_BOLD,
            style="Label.TLabel"
        ).grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.table_var = tk.StringVar(value="Users")
        tables = ["Users", "Departments", "Accesslog"]

        ttk.OptionMenu(
            select,
            self.table_var,
            tables[0],
            *tables,
            style="Custom.TMenubutton"
        ).grid(row=0, column=1, padx=(5, 10), pady=15, sticky="w")

        ttk.Button(
            select,
            text="📋 View Table",
            style="Primary.TButton",
            command=lambda: self.run_query(
                f"SELECT * FROM {self.table_var.get()}",
                tab
            )
        ).grid(row=0, column=2, padx=(0, 15), pady=15)

        self.result_views[tab] = ResultView(tab)

    # ---------------- QUERY EXECUTION ---------------- #

    def run_query(self, query, tab):
        # Run queries in background so the UI doesn’t freeze
        threading.Thread(
            target=self._execute_query,
            args=(query, tab),
            daemon=True     # What's a daemon?
        ).start()

    def _execute_query(self, query, tab):
        try:
            with self.app.app_context():
                results = flaskr.querying.execute_sql_query(
                    query,
                    self.username
                )

            self.root.after(
                0,
                lambda: self.result_views[tab].show_results(results)
            )

        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", str(e))
            )

    # ---------------- STYLING ---------------- #

    def _setup_styles(self):
        # Should probably be moved to their own file but i cba shuffling everything
        self.style.configure(
            "Main.TFrame",
            background=COLOURS["background"]
        )

        self.style.configure(
            "Tab.TFrame",
            background=COLOURS["background"]
        )

        self.style.configure(
            "Header.TFrame",
            background=COLOURS["background"]
        )

        self.style.configure(
            "Card.TFrame",
            background=COLOURS["surface"],
            borderwidth=1,
            relief="flat"
        )

        # Notebook
        self.style.configure(
            "Custom.TNotebook",
            background=COLOURS["background"],
            borderwidth=0
        )

        self.style.configure(
            "Custom.TNotebook.Tab",
            padding=[20, 10],
            font=FONT_BOLD,
            background=COLOURS["surface"]
        )

        self.style.map(
            "Custom.TNotebook.Tab",
            background=[("selected", COLOURS["primary"])],
            foreground=[
                ("selected", "white"),
                ("!selected", COLOURS["text"])
            ]
        )

        # Labels
        self.style.configure(
            "Title.TLabel",
            background=COLOURS["background"],
            foreground=COLOURS["text"]
        )

        self.style.configure(
            "Subtitle.TLabel",
            background=COLOURS["background"],
            foreground=COLOURS["text_secondary"]
        )

        self.style.configure(
            "Label.TLabel",
            background=COLOURS["surface"],
            foreground=COLOURS["text"]
        )

        self.style.configure(
            "Info.TLabel",
            background=COLOURS["surface"],
            foreground=COLOURS["text_secondary"]
        )

        # Buttons
        self.style.configure(
            "Primary.TButton",
            font=FONT_BOLD,
            padding=(20, 10),
            background=COLOURS["primary"],
            foreground="white",
            borderwidth=0
        )

        self.style.map(
            "Primary.TButton",
            background=[("active", COLOURS["primary_hover"])]
        )

        # Entry
        self.style.configure(
            "Custom.TEntry",
            padding=10,
            fieldbackground=COLOURS["surface"],
            background=COLOURS["surface"],
            borderwidth=1
        )

        # Treeview
        self.style.configure(
            "Custom.Treeview",
            font=FONT,
            rowheight=32,
            background=COLOURS["surface"],
            fieldbackground=COLOURS["surface"],
            foreground=COLOURS["text"]
        )

        self.style.configure(
            "Custom.Treeview.Heading",
            font=FONT_BOLD,
            background=COLOURS["background"]
        )

    def run(self):
        self.root.mainloop()


def main(username, flask_app):
    App(username, flask_app).run()


# DEBUG ENTRY POINT
# TODO: remove before submission
if __name__ == "__main__":
    from flaskr import create_app
    App("admin", create_app()).run()
