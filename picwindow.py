#!/usr/bin/python3

from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox

WINDOW_WIDTH = 900
THUMBNAIL_SIZE = 600

class PicWindow(Frame):
    def __init__(self, filenames, master=None):
        Frame.__init__(self, master)

        self.filenames = filenames

        self.master = master
        self.master.title("Select file(s) to delete, ESC to cancel, Enter to finish this file, Q to quit")
        self.pack(fill=BOTH, expand=1)

        # List of indices which have been selected
        self.selected = []

        # Show the picture
        y = 10
        picture = Image.open(filenames[0])
        picture.thumbnail(size=(THUMBNAIL_SIZE, THUMBNAIL_SIZE))
        tk_picture = ImageTk.PhotoImage(picture)
        pic_label = Label(image=tk_picture)
        pic_label.image = tk_picture
        pic_label.place(x=10, y=y)
        y += picture.height + 10

        n = 0
        self.buttons = []
        for filename in filenames:
            # List for press of the 1 (or 2...a...) key
            if n <= 8:
                key = str(n+1)
            else:
                key = chr(88+n)
            self.bind(f"{key}", self.number_key)

            # Create a button and listen for the key for each duplicate filename
            text = f"{key}: {filename}"
            fileButton = Button(self, text=text, command=lambda nn=n: self.select(nn))
            fileButton.place(x=10, y=y)

            y += 40
            n += 1

            self.buttons.append(fileButton)

        # Remember the background colour of the button so we can deselect items
        self.default_button_bg = self.buttons[0].cget("background")

        # Listen for Return, Escape and Q keys
        self.bind("<Return>", self.return_key)
        self.bind("<Escape>", self.escape_key)
        self.bind("Q", self.quit_key)
        self.bind("q", self.quit_key)

        # Resize parent
        master.geometry(f"{WINDOW_WIDTH}x{y}")

        # To ensure we key keypresses
        self.focus_set()

    def number_key(self, event):
        # They key can be 1-9 or a-p
        char = event.char
        if char.isnumeric():
            index = int(event.char) - 1
        else:
            index = ord(char) - 88    # Treat 'a' as 10, i.e. index 9
        self.select(index)

    def return_key(self, event):
        # Prepare the result
        self.results = []
        for index in self.selected:
            self.results.append(self.filenames[index])

        # Close the window
        self.master.destroy()

    def escape_key(self, event):
        # Remove results and stop
        self.results = []
        self.master.destroy()

    def quit_key(self, event):
        # Set results to None and stop
        self.results = None
        self.master.destroy()

    # Select an item.
    # Number is the 0-based index of the item.
    def select(self, index):
        print(f"Index {index}")
        print(f"Selected {self.selected}")
        # If it was already selected, unselect it
        if index in self.selected:
            self.buttons[index].configure(bg=self.default_button_bg)
            self.selected.remove(index)
        else:
            # If we are selecting the last unselected file, double check
            if len(self.selected) >= len(self.filenames)-1:
                print("Checking")
                res = messagebox.askyesno(title="Delete ALL copies?", message=f"Are you sure you want to mark ALL {len(self.filenames)} files for deletion?")
                if not res:
                    return
            self.buttons[index].configure(bg="gray")
            self.selected.append(index)

    
