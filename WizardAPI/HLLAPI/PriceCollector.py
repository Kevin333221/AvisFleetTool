import tkinter as tk
from tkinter import *
from config import *
from coreFunctions import *
from price import *

stations = ["TOS", "TR7", "T1Y", "TO0", "TO7"]

def main():

    # Init tkinter
    root.title("Extract Wizard Prices")
    root.geometry("600x300")
    
    # Create a label widget
    title_label = tk.Label(root, text="Wizard Data Collector", font=("Helvetica", 16), fg="blue", bg="white", padx=10, pady=10)
    title_label.pack()
    
    info_label = tk.Label(root, text="Do not put a date that is more than 1 year ahead of the current date.", font=("Helvetica", 11), fg="red", bg="white", padx=10, pady=10)
    info_label.pack()
    
    # Create a frame to hold the widgets side by side
    frame = tk.Frame(root)
    frame.pack()

    clicked_out = station_out(frame) 
    clicked_in = station_in(frame)

    # Create a date entry widget
    date_label = tk.Label(frame, text="Enter Date Out (Eks: 01JAN24):")
    date_label.grid(row=1, column=0, padx=10, pady=10)
    date_entry = tk.Entry(frame)
    date_entry.grid(row=1, column=1, padx=10, pady=10)
    
    # Create a button widget
    myButton = tk.Button(frame, text="Get Data", command=lambda: getData(date_entry, clicked_out, clicked_in))
    myButton.grid(row=1, column=2, padx=10, pady=10)
    
    # Run the main loop
    root.mainloop()

def station_out(frame):
    
    clicked_out = StringVar()
    
    # initial menu text 
    clicked_out.set("TOS") 
    
    subframe = tk.Frame(frame)
    subframe.grid(row=0, column=0, padx=0, pady=10)
    
    # Create Dropdown menu 
    drop = OptionMenu(subframe, clicked_out, *stations) 
    drop.grid(row=0, column=1, padx=10, pady=10)
    drop_label = tk.Label(subframe, text="Select Station Out:")
    drop_label.grid(row=0, column=0, padx=10, pady=10)
    
    return clicked_out
   
def station_in(frame):
    clicked_in = StringVar()
    
    # initial menu text 
    clicked_in.set("TOS") 
    
    subframe = tk.Frame(frame)
    subframe.grid(row=0, column=1, padx=0, pady=10)
    
    # Create Dropdown menu 
    drop = OptionMenu(subframe, clicked_in, *stations) 
    drop.grid(row=0, column=1, padx=10, pady=10)
    drop_label = tk.Label(subframe, text="Select Station In:")
    drop_label.grid(row=0, column=0, padx=10, pady=10)
    
    return clicked_in  
 
def getData(data, clicked_out, clicked_in):
    
    if data.get() == "" or len(data.get()) != 7 or not data.get()[2:5].isalpha() or not data.get()[5:].isnumeric():
        return
    
    progress_frame = tk.Frame(root)
    progress_frame.pack()
    
    progress_title_label = tk.Label(progress_frame, text="Progress:", font=("Helvetica", 12), fg="blue", bg="white", padx=10, pady=10)
    progress_title_label.grid(row=0, column=0, padx=10, pady=10)
    
    progress_label = tk.Label(progress_frame, text="00/40", font=("Helvetica", 12), fg="green", bg="white", padx=10, pady=10)
    progress_label.grid(row=0, column=1, padx=10, pady=10)
    
    progress_frame.update()
    
    get_prices_for_all_rates("A", f"{data.get()}/1000", clicked_out.get(), clicked_in.get(), ["B", "C", "D", "E", "H", "G", "I", "K", "M", "N"], progress_label)
    
    progress_title_label.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    main()