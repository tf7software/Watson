import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import webbrowser

class SherlockGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Watson Username Search")
        self.create_widgets()
        self.set_output_folder()

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

    def search_usernames(self):
        usernames = self.usernames_entry.get().split(',')
        nsfw = self.nsfw_var.get()

        if not usernames:
            messagebox.showerror("Error", "Please enter at least one username.")
            return

        # Use the full path to the sherlock script
        sherlock_path = "YOUR_SHERLOCK_PATH"
        cmd = [sherlock_path] + usernames
        if nsfw:
            cmd.append("--nsfw")
        cmd.extend(["--folderoutput", self.output_folder])

        # Run Sherlock in a separate thread
        threading.Thread(target=self.run_sherlock, args=(cmd,)).start()

    def run_sherlock(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        found_count = 0

        # Read the output line by line
        for line in process.stdout:
            if "found:" in line:
                found_count += 1
            self.progress_label.config(text=f"Found {found_count} sites with the username(s)")
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
