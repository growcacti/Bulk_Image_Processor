import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import os
import sys
import time
from glob import glob
import json
import threading

BOOKMARK_FILE = "bookmarks.json"
Image.MAX_IMAGE_PIXELS = None

class ImageToolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Tool Suite")
        self.geometry("1400x800")

        # Initialize attributes
        self.image_paths = []
        self.selected_images = []
        self.current_img_path = None
        self.bookmarks = self.load_bookmarks()

        # Top frame for options
        self.frame_top = tk.Frame(self)
        self.frame_top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.btn_browse = tk.Button(self.frame_top, text="Select Directory", command=self.browse_directory)
        self.btn_browse.grid(row=0, column=0, padx=5)

        self.var_recursive = tk.BooleanVar()
        self.check_recursive = tk.Checkbutton(
            self.frame_top, text="Recursive View", variable=self.var_recursive, command=self.update_view
        )
        self.check_recursive.grid(row=0, column=1, padx=5)

        self.btn_clear = tk.Button(self.frame_top, text="Clear Thumbnails", command=self.clear_thumbnails)
        self.btn_clear.grid(row=0, column=2, padx=5)

        self.btn_exit = tk.Button(self.frame_top, text="Exit", command=self.quit_program)
        self.btn_exit.grid(row=0, column=3, padx=5)

        # Bookmark controls
        self.btn_add_bookmark = tk.Button(self.frame_top, text="Add Bookmark", command=self.add_bookmark)
        self.btn_add_bookmark.grid(row=0, column=4, padx=5)

        self.btn_delete_bookmark = tk.Button(self.frame_top, text="Delete Bookmark", command=self.delete_bookmark)
        self.btn_delete_bookmark.grid(row=0, column=5, padx=5)

        self.bookmark_var = tk.StringVar(self)
        self.bookmark_menu = ttk.Combobox(self.frame_top, textvariable=self.bookmark_var, values=list(self.bookmarks.keys()))
        self.bookmark_menu.grid(row=0, column=6, padx=5)
        self.bookmark_menu.bind("<<ComboboxSelected>>", self.goto_bookmark)

        # Frame for thumbnails
        self.frame_left = tk.Frame(self)
        self.frame_left.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Canvas for thumbnails
        self.canvas = tk.Canvas(self.frame_left, bg="white", bd=11)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scroll_y = tk.Scrollbar(self.frame_left, orient="vertical", command=self.canvas.yview)
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.canvas.config(yscrollcommand=self.scroll_y.set)

        # Frame to hold thumbnails inside the canvas
        self.frame_thumbnails = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_thumbnails, anchor="nw")

        # Progress bar for loading indication
        self.progress_bar = ttk.Progressbar(self.frame_left, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        # Frame for file info
        self.frame_right = tk.Frame(self, width=300)
        self.frame_right.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.lbl_info = tk.Label(self.frame_right, text="File Info", anchor="w")
        self.lbl_info.grid(row=0, column=0, sticky="w", pady=5)

        self.txt_info = tk.Text(self.frame_right, height=8, width=40, wrap="word")
        self.txt_info.grid(row=1, column=0, sticky="nsew")

        self.lbl_selected = tk.Label(self.frame_right, text="Selected Images")
        self.lbl_selected.grid(row=2, column=0, sticky="w", pady=5)

        self.listbox_selected = tk.Listbox(self.frame_right, height=15, width=40)
        self.listbox_selected.grid(row=3, column=0, sticky="nsew")

        # Grid weight configuration
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.frame_left.grid_rowconfigure(0, weight=1)
        self.frame_left.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_rowconfigure(1, weight=1)

    def load_bookmarks(self):
        """Load bookmarks from a JSON file."""
        try:
            with open(BOOKMARK_FILE, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_bookmarks(self):
        """Save bookmarks to a JSON file."""
        with open(BOOKMARK_FILE, 'w') as file:
            json.dump(self.bookmarks, file, indent=4)

    def add_bookmark(self):
        """Add the current directory to bookmarks."""
        if not self.current_img_path:
            messagebox.showwarning("No Directory", "Select a directory first.")
            return

        dir_name = os.path.basename(os.path.dirname(self.current_img_path))
        bookmark_name = simpledialog.askstring("Bookmark Name", f"Enter a name for this bookmark ({dir_name}):")
        if bookmark_name:
            self.bookmarks[bookmark_name] = os.path.dirname(self.current_img_path)
            self.bookmark_menu['values'] = list(self.bookmarks.keys())
            self.save_bookmarks()
            messagebox.showinfo("Bookmark Added", f"Bookmark '{bookmark_name}' added successfully.")

    def delete_bookmark(self):
        """Delete the selected bookmark."""
        selected_bookmark = self.bookmark_var.get()
        if not selected_bookmark:
            messagebox.showwarning("No Bookmark Selected", "Select a bookmark to delete.")
            return

        del self.bookmarks[selected_bookmark]
        self.bookmark_menu['values'] = list(self.bookmarks.keys())
        self.bookmark_var.set('')
        self.save_bookmarks()
        messagebox.showinfo("Bookmark Deleted", f"Bookmark '{selected_bookmark}' deleted successfully.")

    def goto_bookmark(self, event):
        """Go to the selected bookmark directory."""
        selected_bookmark = self.bookmark_var.get()
        if selected_bookmark and selected_bookmark in self.bookmarks:
            self.load_images(self.bookmarks[selected_bookmark])

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if not directory:
            return

        # Start the image loading in a separate thread
        threading.Thread(target=self.load_images, args=(directory,), daemon=True).start()

    def load_images(self, directory):
        extensions = ('*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.tiff')
        search_pattern = '**/*' if self.var_recursive.get() else '*'

        self.image_paths = []
        for ext in extensions:
            self.image_paths.extend(glob(os.path.join(directory, search_pattern, ext), recursive=self.var_recursive.get()))

        if not self.image_paths:
            messagebox.showinfo("No Images Found", "No images found in the selected directory.")
            return

        self.display_thumbnails()

    def display_thumbnails(self):
        self.clear_thumbnails()
        self.progress_bar["maximum"] = len(self.image_paths)

        for idx, img_path in enumerate(self.image_paths):
            try:
                img = Image.open(img_path)
                img.thumbnail((100, 100))
                tk_img = ImageTk.PhotoImage(img)

                frame = tk.Frame(self.frame_thumbnails, bd=2, relief="ridge")
                frame.grid(row=idx // 6, column=idx % 6, padx=5, pady=5)

                lbl_img = tk.Label(frame, image=tk_img)
                lbl_img.image = tk_img
                lbl_img.grid(row=0, column=0)

                lbl_info = tk.Label(frame, text=os.path.basename(img_path), wraplength=100, anchor="w")
                lbl_info.grid(row=1, column=0, sticky="ew")

                lbl_img.bind("<Enter>", lambda e, path=img_path: self.show_file_info(path))
                lbl_img.bind("<Double-1>", lambda e, path=img_path: self.add_to_selection(path))

                # Update the progress bar
                self.progress_bar.step(1)
                self.progress_bar.update_idletasks()

            except Exception as e:
                print(f"Error loading image {img_path}: {e}")

        self.frame_thumbnails.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.progress_bar["value"] = 0

    def clear_thumbnails(self):
        """Clears the currently displayed thumbnails."""
        for widget in self.frame_thumbnails.winfo_children():
            widget.destroy()

    def show_file_info(self, img_path):
        file_size = os.path.getsize(img_path) / 1024
        last_modified = time.ctime(os.path.getmtime(img_path))

        info_text = (
            f"Path: {img_path}\n"
            f"Size: {file_size:.2f} KB\n"
            f"Last Modified: {last_modified}"
        )

        self.txt_info.delete(1.0, tk.END)
        self.txt_info.insert(tk.END, info_text)
        self.current_img_path = img_path

    def add_to_selection(self, img_path):
        if img_path not in self.selected_images:
            self.selected_images.append(img_path)
            self.listbox_selected.insert(tk.END, os.path.basename(img_path))



    
    def merge_images(self):
        if len(self.selected_images) < 2:
            messagebox.showwarning("Not Enough Images", "Select at least two images to merge.")
            return

        images = [Image.open(img) for img in self.selected_images]
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)

        merged_image = Image.new('RGB', (total_width, max_height))
        x_offset = 0

        for img in images:
            merged_image.paste(img, (x_offset, 0))
            x_offset += img.width

        self.display_merged_image(merged_image)

    def display_merged_image(self, image):
        img = image.resize((800, 600))
        tk_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(400, 300, anchor=tk.CENTER, image=tk_img)
        self.canvas.image = tk_img

    def build_sprite_sheet(self):
        if not self.selected_images:
            messagebox.showwarning("No Images", "Select images to create a sprite sheet.")
            return

        try:
            columns = simpledialog.askinteger("Columns", "Enter number of columns:", minvalue=1)
            if not columns:
                return

            rows = (len(self.selected_images) + columns - 1) // columns
            img_width, img_height = Image.open(self.selected_images[0]).size

            sprite_sheet = Image.new('RGBA', (img_width * columns, img_height * rows))
            for idx, img_path in enumerate(self.selected_images):
                img = Image.open(img_path)
                row, col = divmod(idx, columns)
                sprite_sheet.paste(img, (col * img_width, row * img_height))

            self.display_merged_image(sprite_sheet)
            messagebox.showinfo("Sprite Sheet Complete", "Sprite sheet built successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def quit_program(self):
        """Exits the program."""
        self.destroy()
        sys.exit()

    def update_view(self):
        self.browse_directory()

if __name__ == "__main__":
    app = ImageToolApp()
    app.mainloop()
