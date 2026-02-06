import os
import re
import shutil
import tkinter as tk
import traceback
from tkinter import filedialog, messagebox, ttk


def get_base_name(filename):
    """Strip leading numbers (and optional space) from a filename to get the base name.

    Examples:
        "1 image.png"          -> "image.png"
        "12 image of potato.png" -> "image of potato.png"
        "image.png"            -> "image.png"
        "123image.png"         -> "image.png"
    """
    return re.sub(r"^\d+\s*", "", filename)


def find_duplicate_groups(folder):
    """Group files by their base name (filename with leading numbers stripped).

    Returns a dict mapping base_name -> list of full filenames, only for groups
    with more than one file (i.e. actual duplicates).
    """
    folder = os.path.normpath(os.path.abspath(folder))
    groups = {}
    for fname in sorted(os.listdir(folder)):
        fpath = os.path.join(folder, fname)
        if not os.path.isfile(fpath):
            continue
        base = get_base_name(fname)
        if not base:
            continue
        groups.setdefault(base, []).append(fname)

    # Only return groups that have duplicates
    return {base: files for base, files in groups.items() if len(files) > 1}


# -- Color palette --
BG = "#f5f5f5"
FG = "#1a1a1a"
FG_SECONDARY = "#555555"
ACCENT = "#4a90d9"
BTN_BG = "#ffffff"
LOG_BG = "#ffffff"
BORDER = "#d0d0d0"
SEP = "#c8c8c8"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("REMOVE DUPLICATE IMAGES")
        self.geometry("1024x768")
        self.minsize(500, 450)
        self.configure(bg=BG)

        self.selected_folder = None

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # General frame background
        self.style.configure("TFrame", background=BG)

        # Labels
        self.style.configure(
            "TLabel",
            background=BG,
            foreground=FG,
            font=("Helvetica", 13),
        )
        self.style.configure(
            "Secondary.TLabel",
            background=BG,
            foreground=FG_SECONDARY,
            font=("Helvetica", 12),
        )
        self.style.configure(
            "Heading.TLabel",
            background=BG,
            foreground=FG,
            font=("Helvetica", 13, "bold"),
        )

        # Buttons
        self.style.configure(
            "TButton",
            font=("Helvetica", 13),
            padding=(12, 8),
        )
        self.style.configure(
            "Accent.TButton",
            font=("Helvetica", 13, "bold"),
            padding=(12, 10),
        )

        # Checkbuttons
        self.style.configure(
            "TCheckbutton",
            background=BG,
            foreground=FG,
            font=("Helvetica", 13),
        )

        # Separator
        self.style.configure("TSeparator", background=SEP)

    def _build_ui(self):
        pad_x = 16

        # --- Select Folder button ---
        btn_select = ttk.Button(
            self,
            text="Select Folder",
            command=self._select_folder,
            style="TButton",
        )
        btn_select.pack(fill="x", padx=pad_x, pady=(12, 6))

        # --- Selected Folder label ---
        self.lbl_folder = ttk.Label(
            self,
            text="Selected Folder: None",
            style="Heading.TLabel",
        )
        self.lbl_folder.pack(fill="x", padx=pad_x, pady=(0, 6))

        # --- Log area ---
        log_frame = ttk.Frame(self)
        log_frame.pack(fill="both", expand=True, padx=pad_x, pady=(0, 6))

        self.log_text = tk.Text(
            log_frame,
            wrap="word",
            state="disabled",
            bg=LOG_BG,
            fg=FG,
            font=("Menlo", 11),
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            padx=8,
            pady=8,
            height=4,
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        # --- Status labels ---
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=pad_x, pady=(0, 4))

        self.lbl_images = ttk.Label(
            status_frame,
            text="Images Processed: 0 / 0",
            style="Secondary.TLabel",
        )
        self.lbl_images.pack(side="left")

        self.lbl_folders = ttk.Label(
            status_frame,
            text="Folders Processed: 0 / 0",
            style="Secondary.TLabel",
        )
        self.lbl_folders.pack(side="right")

        # --- Separator ---
        sep = ttk.Separator(self, orient="horizontal")
        sep.pack(fill="x", padx=pad_x, pady=(4, 6))

        # --- Options ---
        options_frame = ttk.Frame(self)
        options_frame.pack(fill="x", padx=pad_x)

        # Keep N duplicates
        row_keep = ttk.Frame(options_frame)
        row_keep.pack(fill="x", pady=(0, 6), anchor="w")

        ttk.Label(row_keep, text="Keep", style="TLabel").pack(side="left")

        self.keep_var = tk.IntVar(value=1)
        self.keep_spin = tk.Spinbox(
            row_keep,
            from_=1,
            to=100,
            width=4,
            textvariable=self.keep_var,
            font=("Helvetica", 13),
            relief="flat",
            borderwidth=1,
            bg=BTN_BG,
            fg=FG,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self.keep_spin.pack(side="left", padx=(8, 8))

        ttk.Label(row_keep, text="duplicate(s)", style="TLabel").pack(side="left")

        # Mode selection (mutually exclusive)
        self.mode_var = tk.StringVar(value="transfer")

        self.style.configure(
            "TRadiobutton",
            background=BG,
            foreground=FG,
            font=("Helvetica", 13),
        )

        rb_transfer = ttk.Radiobutton(
            options_frame,
            text="Transfer duplicates to NEW folder",
            variable=self.mode_var,
            value="transfer",
            style="TRadiobutton",
        )
        rb_transfer.pack(fill="x", pady=(0, 4), anchor="w")

        rb_remove = ttk.Radiobutton(
            options_frame,
            text="Remove duplicates",
            variable=self.mode_var,
            value="remove",
            style="TRadiobutton",
        )
        rb_remove.pack(fill="x", pady=(0, 4), anchor="w")

        # --- Start Processing button ---
        self.btn_start = ttk.Button(
            self,
            text="Start Processing",
            command=self._start_processing,
            style="Accent.TButton",
        )
        self.btn_start.pack(fill="x", padx=pad_x, pady=(8, 12))

    # --- Helpers ---

    def _log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self.update_idletasks()

    def _select_folder(self):
        folder = filedialog.askdirectory(title="Select folder with images")
        if folder:
            folder = os.path.normpath(os.path.abspath(folder))
            self.selected_folder = folder
            self.lbl_folder.configure(text=f"Selected Folder: {folder}")
            self._log(f"Folder selected: {folder}")

            # Reset counters
            self.lbl_images.configure(text="Images Processed: 0 / 0")
            self.lbl_folders.configure(text="Folders Processed: 0 / 0")

    def _start_processing(self):
        if not self.selected_folder:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return

        if not os.path.isdir(self.selected_folder):
            messagebox.showerror(
                "Folder not found",
                f"The selected folder no longer exists:\n{self.selected_folder}",
            )
            return

        try:
            keep_count = self.keep_var.get()
        except tk.TclError:
            messagebox.showwarning("Invalid value", "Keep count must be a number.")
            return
        mode = self.mode_var.get()

        if keep_count < 1:
            messagebox.showwarning("Invalid value", "Keep count must be at least 1.")
            return

        self.btn_start.configure(state="disabled")
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

        try:
            self._process(self.selected_folder, keep_count, mode)
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f"Error: {e}\n{tb}")
            messagebox.showerror("Error", str(e))
        finally:
            self.btn_start.configure(state="normal")

    def _process(self, root_folder, keep_count, mode):
        root_folder = os.path.normpath(os.path.abspath(root_folder))

        # NEW folder is a sibling of the selected folder
        new_root = os.path.join(os.path.dirname(root_folder), "NEW")

        # Collect all folders to process (root + subfolders), skip "NEW" folders
        folders_to_process = []
        for dirpath, dirnames, _filenames in os.walk(root_folder):
            dirnames[:] = [d for d in dirnames if d != "NEW"]
            folders_to_process.append(os.path.normpath(dirpath))

        # Pre-scan: count total images and folders with duplicates
        folder_groups = []
        total_images = 0
        for folder in folders_to_process:
            groups = find_duplicate_groups(folder)
            if groups:
                folder_groups.append((folder, groups))
                total_images += sum(len(files) for files in groups.values())

        total_folders = len(folder_groups)

        if not folder_groups:
            self._log("No duplicate groups found in any folder.")
            self.lbl_images.configure(text="Images Processed: 0 / 0")
            self.lbl_folders.configure(text="Folders Processed: 0 / 0")
            return

        self.lbl_images.configure(text=f"Images Processed: 0 / {total_images}")
        self.lbl_folders.configure(text=f"Folders Processed: 0 / {total_folders}")

        processed_images = 0
        processed_folders = 0

        for folder, groups in folder_groups:
            processed_folders += 1
            self._log(f"\n--- Folder: {folder} ---")

            # For transfer mode, compute the mirrored subfolder inside NEW
            dup_folder = None
            if mode == "transfer":
                rel = os.path.relpath(folder, root_folder)
                dup_folder = os.path.join(new_root, rel) if rel != "." else new_root
                os.makedirs(dup_folder, exist_ok=True)
                self._log(f"Destination folder: {dup_folder}")

            for base, files in groups.items():
                self._log(f"\nGroup: '{base}' ({len(files)} files)")

                files_sorted = sorted(files)
                to_keep = files_sorted[:keep_count]
                extras = files_sorted[keep_count:]

                for f in to_keep:
                    self._log(f"  Keeping: {f}")
                    processed_images += 1
                    self.lbl_images.configure(
                        text=f"Images Processed: {processed_images} / {total_images}"
                    )
                    self.update_idletasks()

                for f in extras:
                    src = os.path.join(folder, f)

                    try:
                        if mode == "transfer":
                            dst = os.path.join(dup_folder, f)
                            shutil.move(src, dst)
                            self._log(f"  Moved to NEW: {f}")
                        else:
                            os.remove(src)
                            self._log(f"  Removed: {f}")
                    except FileNotFoundError:
                        self._log(f"  Skipped (file not found): {f}")
                    except OSError as e:
                        self._log(f"  Error processing {f}: {e}")

                    processed_images += 1
                    self.lbl_images.configure(
                        text=f"Images Processed: {processed_images} / {total_images}"
                    )
                    self.update_idletasks()

            self.lbl_folders.configure(
                text=f"Folders Processed: {processed_folders} / {total_folders}"
            )
            self.update_idletasks()

        self._log("\nDone!")
        messagebox.showinfo("Done", "Processing complete.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
