import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk
from excel_to_json_logic import process_excel_to_json
from pom_updater_logic import update_versions_in_project

CONFIG_PATH = "config.json"

class AliceDependencyUpdater(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Alice Dependency Updater")
        self.geometry("860x600")

        self.excel_path = ""
        self.project_dir = ""
        self.backend_data = []
        self.module_data = []
        self.current_theme = "dark"
        self.preview_mode = tk.BooleanVar(value=False)

        self.style = ttk.Style()
        self.configure_theme(self.current_theme)

        self.status_var = tk.StringVar(value="Ready")
        self.create_widgets()
        self.load_config()

    def configure_theme(self, theme):
        bg, fg = ("#2e2e2e", "#ffffff") if theme == "dark" else ("#f0f0f0", "#000000")
        self.configure(bg=bg)
        self.style.theme_use('clam' if theme == "dark" else 'default')
        self.style.configure(".", background=bg, foreground=fg, font=("Segoe UI", 10))
        self.style.configure("TButton", padding=6, relief="flat", background=bg, foreground=fg)
        self.style.map("TButton", background=[("active", "#555" if theme == "dark" else "#ddd")])

    def create_widgets(self):
        # Top bar
        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=5)
        ttk.Label(top, text="Alice Dependency Updater", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(top, text="🔍 Preview Mode", variable=self.preview_mode).pack(side=tk.RIGHT, padx=10)
        self.theme_btn = ttk.Button(top, text="🌙", width=3, command=self.toggle_theme)
        self.theme_btn.pack(side=tk.RIGHT)

        # Input area
        input_frame = ttk.Frame(self)
        input_frame.pack(padx=10, pady=10, fill=tk.X)

        # Excel file
        ttk.Label(input_frame, text="📂 Excel File:").grid(row=0, column=0, sticky="w")
        self.excel_label = ttk.Label(input_frame, text="No file selected", width=50)
        self.excel_label.grid(row=0, column=1, sticky="w", padx=5)
        self.excel_btn = ttk.Button(input_frame, text="Browse", command=self.select_excel)
        self.excel_btn.grid(row=0, column=2)

        # Project folder
        ttk.Label(input_frame, text="📁 Project Dir:").grid(row=1, column=0, sticky="w", pady=(10,0))
        self.project_label = ttk.Label(input_frame, text="No folder selected", width=50)
        self.project_label.grid(row=1, column=1, sticky="w", padx=5, pady=(10,0))
        self.project_btn = ttk.Button(input_frame, text="Browse", command=self.select_project_dir)
        self.project_btn.grid(row=1, column=2, pady=(10,0))

        self.git_btn = ttk.Button(input_frame, text="🐙 Git", command=self.open_git_console)
        self.git_btn.grid(row=1, column=3, padx=(10, 0), pady=(10, 0))
        self.git_btn.grid_remove()

        # Run update
        self.run_btn = ttk.Button(input_frame, text="🚀 Run Update", command=self.run_update)
        self.run_btn.grid(row=2, column=2, pady=15, sticky="e")

        # Output area
        log_frame = ttk.Frame(self)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        self.output_area = tk.Text(log_frame, height=15, wrap=tk.WORD, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10))
        self.output_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_area.config(state=tk.DISABLED)

        scroll = ttk.Scrollbar(log_frame, command=self.output_area.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_area.config(yscrollcommand=scroll.set)

        ttk.Button(self, text="🧹 Clear Log", command=self.clear_output).pack(pady=(0, 5))
        ttk.Label(self, textvariable=self.status_var, anchor="w", relief="sunken").pack(side=tk.BOTTOM, fill=tk.X)

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.configure_theme(self.current_theme)
        self.theme_btn.config(text="☀️" if self.current_theme == "light" else "🌙")
        self.save_config()

    def log_output(self, message):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)
        self.status_var.set("Last log: " + message[:80])

    def clear_output(self):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete("1.0", tk.END)
        self.output_area.config(state=tk.DISABLED)
        self.status_var.set("Log cleared")

    def select_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if path:
            try:
                output_paths = process_excel_to_json(path)
                self.excel_path = path
                self.excel_label.config(text="✅ " + os.path.basename(path))
                self.log_output("Excel loaded. ")
                with open(output_paths[0], 'r', encoding='utf-8') as f:
                    self.backend_data = json.load(f)['data']
                with open(output_paths[1], 'r', encoding='utf-8') as f:
                    self.module_data = json.load(f)['data']
                self.save_config()
            except Exception as e:
                self.log_output("❌ Error loading Excel: " + str(e))

    def select_project_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.project_dir = path
            self.project_label.config(text="✅ " + os.path.basename(path))
            self.git_btn.grid()
            self.log_output("Project folder selected: " + self.project_dir)
            self.save_config()

    def open_git_console(self):
        if os.name == 'nt':
            subprocess.Popen(["start", "cmd", "/K", "cd /d " + self.project_dir], shell=True)
        else:
            self.log_output("⚠ Git console is only supported on Windows.")

    def run_update(self):
        if not self.backend_data or not self.module_data:
            self.log_output("⚠ Please load an Excel file first.")
            return
        if not self.project_dir:
            self.log_output("⚠ Please select a Maven project folder.")
            return
        try:
            changes = update_versions_in_project(
                self.project_dir,
                self.backend_data,
                self.module_data,
                preview=self.preview_mode.get()
            )
            total = sum(len(c['changes']) for c in changes)
            mode = "🔍 Preview" if self.preview_mode.get() else "✅ Update"
            self.log_output(f"{mode}: {total} changes")
            for change in changes:
                self.log_output(f"\n".join(change['changes']))
        except Exception as e:
            self.log_output("❌ Error during update: " + str(e))

    def save_config(self):
        cfg = {
            "excel_path": self.excel_path,
            "project_dir": self.project_dir,
            "theme": self.current_theme,
            "preview": self.preview_mode.get()
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f)

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                cfg = json.load(f)
                self.excel_path = cfg.get("excel_path", "")
                self.project_dir = cfg.get("project_dir", "")
                self.current_theme = cfg.get("theme", "dark")
                self.preview_mode.set(cfg.get("preview", False))
                if self.excel_path:
                    self.excel_label.config(text="✅ " + os.path.basename(self.excel_path))
                if self.project_dir:
                    self.project_label.config(text="✅ " + os.path.basename(self.project_dir))
                    self.git_btn.grid()
                self.configure_theme(self.current_theme)

if __name__ == "__main__":
    app = AliceDependencyUpdater()
    app.mainloop()