import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import threading
import os
import webbrowser

class SherlockPathPopup:
    def __init__(self, parent):
        self.parent = parent
        self.popup = tk.Toplevel(parent.root)
        self.popup.title("Sherlock Path")
        
        self.path_label = tk.Label(self.popup, text="Paste Sherlock Path:")
        self.path_label.pack(pady=5)
        
        self.path_entry = tk.Entry(self.popup, width=50)
        self.path_entry.pack(pady=5)
        
        self.ok_button = tk.Button(self.popup, text="OK", command=self.set_sherlock_path)
        self.ok_button.pack(pady=5)
        
    def set_sherlock_path(self):
        path = self.path_entry.get().strip()
        if path:
            self.parent.save_sherlock_path(path)
            self.popup.destroy()
            self.parent.search_usernames()  # Start the search after setting the path
        else:
            messagebox.showerror("Error", "Please enter a valid path.")


class SherlockGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Watson Username Search")
        self.create_widgets()
        self.set_output_folder()
        self.load_sherlock_path()

    def create_widgets(self):
        # Info label with hyperlink
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)

        info_text = tk.Text(info_frame, height=1, width=60, bd=0, bg=self.root.cget('bg'), cursor="hand2")
        info_text.tag_configure("sherlock", foreground="lightblue", underline=True)
        info_text.insert(tk.END, "© TwentyFour7 Software, uses ")
        info_text.insert(tk.END, "SHERLOCK", "sherlock")
        info_text.insert(tk.END, "\n")
        info_text.config(state=tk.DISABLED)
        info_text.pack(side=tk.LEFT)
        info_text.bind("<Button-1>", lambda e: self.open_url("https://github.com/sherlock-project/sherlock"))

        # Usernames entry
        self.usernames_label = tk.Label(self.root, text="Usernames (comma-separated):")
        self.usernames_label.pack(pady=5)
        self.usernames_entry = tk.Entry(self.root, width=50)
        self.usernames_entry.pack(pady=5)

        # NSFW checkbox
        self.nsfw_var = tk.BooleanVar()
        self.nsfw_check = tk.Checkbutton(self.root, text="Include NSFW sites", variable=self.nsfw_var)
        self.nsfw_check.pack(pady=5)

        # Search button
        self.search_button = tk.Button(self.root, text="Search", command=self.search_usernames)
        self.search_button.pack(pady=20)

        # Progress label
        self.progress_label = tk.Label(self.root, text="")
        self.progress_label.pack(pady=5)

        # Output text area
        self.output_text = tk.Text(self.root, height=20, width=80)
        self.output_text.pack(pady=5)

    def set_output_folder(self):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.output_folder = os.path.join(desktop_path, "WatsonSearches")

        # Create the SherlockGUI folder on the Desktop if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def open_url(self, url):
        webbrowser.open_new(url)

    def load_sherlock_path(self):
        path_file = "PATH.watson"
        if os.path.exists(path_file):
            with open(path_file, "r") as f:
                self.sherlock_path = f.read().strip()
        else:
            self.sherlock_path = None

    def save_sherlock_path(self, path):
        path_file = "PATH.watson"
        with open(path_file, "w") as f:
            f.write(path)

    def search_usernames(self):
        if not self.sherlock_path:
            SherlockPathPopup(self)
            return

        usernames = self.usernames_entry.get().split(',')
        nsfw = self.nsfw_var.get()

        if not usernames:
            messagebox.showerror("Error", "Please enter at least one username.")
            return

        cmd = [self.sherlock_path] + usernames
        if nsfw:
            cmd.append("--nsfw")
        cmd.extend(["--folderoutput", self.output_folder])

        threading.Thread(target=self.run_sherlock, args=(cmd,)).start()

    def run_sherlock(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        found_count = 0

        # Read the output line by line
        for line in process.stdout:
            if "found:" in line:
                found_count += 1
            
            self.output_text.insert(tk.END, line)
            self.output_text.see(tk.END)

        # Capture any errors
        stderr = process.stderr.read()
        if stderr:
            self.output_text.insert(tk.END, "\nErrors:\n")
            self.output_text.insert(tk.END, stderr)

if __name__ == "__main__":
    root = tk.Tk()
    app = SherlockGUI(root)
    root.mainloop()
