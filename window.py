import matplotlib as matplot
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbat2Tk)
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk

class App():
    def __init__(self):
        self.root = tk.Tk()

        self.window_width = 300
        self.window_height = 200
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        centre_x = int(self.screen_width/2 - self.window_width/2)
        centre_y = int(self.screen_height/2 - self.window_height/2)

        # Set up window
        self.root.title("Data Analyser | Carpal Inc.")
        self.root.geometry(f"{self.window_width}x{self.window_height}+{centre_x}+{centre_y}")
        self.root.resizable(True, True)
        self.root.iconbitmap("assets/main_window.ico")

        self.setup_buttons()

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
        self.tab_control.grid(row=1, columnspan=1)

        self.style = ttk.Style()
        self.style.configure("TNotebook.Tab", padding=(20, 5))


    
    def setup_buttons(self):
        # Logout button
        #TODO: Style this button to look not so out-of-place in tab control
        #TODO: Where's my button? :(
        self.logout_icon = tk.PhotoImage(file="assets/logout.png").subsample(25, 25)

        self.logout_button = tk.Button(
            self.root,
            image=self.logout_icon,
            text="Log Out",
            compound=tk.LEFT,
            command=self.root.destroy
        ).grid(row=1)


    def setup_home_tab(self):
        home_plot_button = tk.Button(master = self.root,
                                     height = 2,
                                     width = 10,
                                     text = "Plot")


    def run(self):
        self.root.mainloop()



def main():
    tkWindow = App()
    tkWindow.run()


if __name__ == "__main__":
    main()