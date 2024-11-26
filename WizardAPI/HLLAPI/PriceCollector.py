import tkinter as tk
from tkinter import *
from config import *
from coreFunctions import *
from price import *

# List of station codes
stations = ["TOS", "TR7", "T1Y", "TO0", "TO7"]

# Styling variables
BG_COLOR = "#f4f4f4"  # Background color
FRAME_BG = "#ffffff"  # Frame background
TITLE_COLOR = "#2c3e50"  # Title text color
INFO_COLOR = "#e74c3c"  # Info text color
LABEL_COLOR = "#34495e"  # Label text color
BUTTON_COLOR = "#3498db"  # Button background
BUTTON_TEXT_COLOR = "#ffffff"  # Button text color
DROPDOWN_COLOR = "#ecf0f1"  # Dropdown background

# Main function to set up the GUI
def main():
    # Initialize tkinter root window
    root.title("Extract Wizard Prices")
    root.geometry("700x400")
    root.configure(bg=BG_COLOR)

    # Title label
    title_label = tk.Label(
        root,
        text="Wizard Data Collector",
        font=("Helvetica", 20, "bold"),
        fg=TITLE_COLOR,
        bg=BG_COLOR,
        padx=10,
        pady=20
    )
    title_label.pack()

    # Information label
    info_label = tk.Label(
        root,
        text="Do not put a date that is more than 1 year ahead of the current date.",
        font=("Helvetica", 12, "italic"),
        fg=INFO_COLOR,
        bg=BG_COLOR,
        padx=10,
        pady=10
    )
    info_label.pack()

    # Frame for organizing widgets
    frame = tk.Frame(root, bg=FRAME_BG, relief="ridge", borderwidth=2)
    frame.pack(padx=20, pady=20)

    # Dropdown menus for station selection
    clicked_out = station_out(frame)
    clicked_in = station_in(frame)

    # Date entry
    date_label = tk.Label(
        frame,
        text="Enter Date Out (e.g., 01JAN24):",
        font=("Helvetica", 11),
        fg=LABEL_COLOR,
        bg=FRAME_BG
    )
    date_label.grid(row=1, column=0, padx=10, pady=10)

    date_entry = tk.Entry(frame, font=("Helvetica", 12), relief="solid", bd=1)
    date_entry.grid(row=1, column=1, padx=10, pady=10)

    # Button to trigger data collection
    my_button = tk.Button(
        frame,
        text="Get Data",
        font=("Helvetica", 12, "bold"),
        bg=BUTTON_COLOR,
        fg=BUTTON_TEXT_COLOR,
        activebackground="#2980b9",
        activeforeground=BUTTON_TEXT_COLOR,
        command=lambda: get_data(date_entry, clicked_out, clicked_in),
        relief="flat",
        padx=15,
        pady=5
    )
    my_button.grid(row=1, column=2, padx=10, pady=10)

    # Run the main event loop
    root.mainloop()

# Function to create a dropdown menu for "Station Out"
def station_out(frame):
    clicked_out = StringVar()
    clicked_out.set("TOS")  # Default value

    subframe = tk.Frame(frame, bg=FRAME_BG)
    subframe.grid(row=0, column=0, padx=0, pady=10)

    drop_label = tk.Label(
        subframe,
        text="Select Station Out:",
        font=("Helvetica", 11),
        fg=LABEL_COLOR,
        bg=FRAME_BG
    )
    drop_label.grid(row=0, column=0, padx=10, pady=10)

    drop = OptionMenu(subframe, clicked_out, *stations)
    drop.config(font=("Helvetica", 11), bg=DROPDOWN_COLOR, relief="flat", highlightthickness=1, bd=1)
    drop.grid(row=0, column=1, padx=10, pady=10)

    return clicked_out

# Function to create a dropdown menu for "Station In"
def station_in(frame):
    clicked_in = StringVar()
    clicked_in.set("TOS")  # Default value

    subframe = tk.Frame(frame, bg=FRAME_BG)
    subframe.grid(row=0, column=1, padx=0, pady=10)

    drop_label = tk.Label(
        subframe,
        text="Select Station In:",
        font=("Helvetica", 11),
        fg=LABEL_COLOR,
        bg=FRAME_BG
    )
    drop_label.grid(row=0, column=0, padx=10, pady=10)

    drop = OptionMenu(subframe, clicked_in, *stations)
    drop.config(font=("Helvetica", 11), bg=DROPDOWN_COLOR, relief="flat", highlightthickness=1, bd=1)
    drop.grid(row=0, column=1, padx=10, pady=10)

    return clicked_in

# Function to handle data retrieval
def get_data(date_entry, clicked_out, clicked_in):
    date = date_entry.get()
    if not (date and len(date) == 7 and date[2:5].isalpha() and date[5:].isnumeric()):
        return  # Invalid input

    # Frame for displaying progress
    progress_frame = tk.Frame(root, bg=BG_COLOR)
    progress_frame.pack()

    progress_title_label = tk.Label(
        progress_frame,
        text="Progress:",
        font=("Helvetica", 12),
        fg=TITLE_COLOR,
        bg=BG_COLOR,
        padx=10,
        pady=10
    )
    progress_title_label.grid(row=0, column=0, padx=10, pady=10)

    progress_label = tk.Label(
        progress_frame,
        text="00/40",
        font=("Helvetica", 12),
        fg="green",
        bg=BG_COLOR,
        padx=10,
        pady=10
    )
    progress_label.grid(row=0, column=1, padx=10, pady=10)

    progress_frame.update()

    # Call the core function to get prices
    get_prices_for_all_rates(
        "A",
        f"{date}/1000",
        clicked_out.get(),
        clicked_in.get(),
        ["B", "C", "D", "E", "H", "G", "I", "K", "M", "N"],
        progress_label
    )

    # Cleanup progress labels after completion
    progress_title_label.destroy()

# Initialize and run the application
if __name__ == "__main__":
    root = tk.Tk()
    main()
