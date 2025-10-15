import os
import sys
import ctypes
from parser import find_cosmetics
import vpk
import json
import shutil
import atexit
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Variables & paths
tf2_default_dir = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2"
tf2_dir = ""
target_cosmetics = []
all_cosmetics = []
all_names = []

mod_folder = Path().absolute() / "Cosmetic-Mod-Staging"
program_data = Path().absolute() / "Cosmetic Disabler Data"
cosmetic_data = program_data / "data2"
replacement_folder = Path().absolute() / "Replacement Files"

for folder in (mod_folder, program_data):
    folder.mkdir(exist_ok=True)

if not replacement_folder.exists():
    messagebox.showerror("Missing Folder", f"Replacement model files not found.\nFolder missing at: {replacement_folder}\nThis Software will not work. Please re-download this program from Github or move 'Replacement Files' to the correct location.")


# Functions

if sys.platform == "win32":  # Force custom app ID to ensure program icon usage
    app_id = u"TF2CosmeticDisabler.app"
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass


def resource_path(relative_path): # Check whether program has been compiled with pyinstaller or is simply running from a straight .py file
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def delete_vpk_folder():
    if mod_folder.exists():
        shutil.rmtree(mod_folder)


atexit.register(delete_vpk_folder) # Delete VPK staging folder upon program termination


def save_cosmetics(): # Save disabled cosmetics to file
    with open(cosmetic_data, "w") as file:
        json.dump(target_cosmetics, file)
        messagebox.showinfo("Saved", "Disabled cosmetics saved successfully.")


def on_close(): # Prompt save when user wants to quit program
    if messagebox.askyesno("Saving", "Do you want to save before quitting?"):
        save_cosmetics()
        root.destroy()
        return
    root.destroy()


def get_custom_dir(): # Prompt user for custom TF2 directory
    global tf2_dir
    folder = filedialog.askdirectory(title="Select Team Fortress 2 folder")
    if not folder:
        return
    if os.path.exists(os.path.join(folder, "tf", "scripts", "items", "items_game.txt")):
        tf2_dir = folder
        with open(program_data / "data", "w") as f:
            f.write(tf2_dir)
        messagebox.showinfo("TF2 Folder Set", f"TF2 directory set to:\n{tf2_dir}")
        tf2_dir_label.config(text=tf2_dir)
        load_cosmetics()
    else:
        messagebox.showerror("Error", "Invalid TF2 directory. 'tf.exe' not found!")


def on_all_cosmetics_double_click(event): # Run when cosmetic in enabled list is interacted with
    selection = cosmetic_listbox.curselection()
    if not selection:
        return
    name = cosmetic_listbox.get(selection[0])
    if name in [c["name"] for c in target_cosmetics]:
        messagebox.showinfo("Already Disabled", f"{name} is already disabled.")
        return
    answer = messagebox.askyesno("Disable Cosmetic", f"Do you want to disable '{name}'?")
    if answer:
        cosmetic_obj = next((c for c in all_cosmetics if c.get("name") == name), None)
        if cosmetic_obj:
            target_cosmetics.append(cosmetic_obj)
            update_disabled_list()


def on_disabled_double_click(event): # Run when cosmetic in disabled list is interacted with
    selection = disabled_listbox.curselection()
    if not selection:
        return
    name = disabled_listbox.get(selection[0])
    answer = messagebox.askyesno("Enable Cosmetic", f"Do you want to enable '{name}'?")
    if answer:
        index = selection[0]
        target_cosmetics.pop(index)
        update_disabled_list()


def create_vpk(): # Process disabled cosmetic filepaths and create VPK file
    cosmetic_paths_final = []

    replace_bodygroups = messagebox.askyesno("Bodygroup Replacements",
                                             "Do you want to replace cosmetic models with stock models when applicable? (Soldier helmet, Sniper hat, etc)\n\nPros:\n\n* Players wearing a disabled cosmetic that affects the hat bodygroup will be wearing the default headwear instead of nothing.\n\nCons:\n\n* If a player wears multiple cosmetics and atleast one of them replaces the default headwear, models have a chance to clip and look ugly.\n\n* A disabled cosmetic replacing Engineer's hard hat will cause the hard hat to have weird physics upon death.")

    for cosmetic in target_cosmetics:
        paths = cosmetic.get("paths", [])
        is_phy_bodygroup = cosmetic.get("phy_bodygroup", False)
        for path in paths:
            main, ext = os.path.splitext(path)
            cosmetic_paths_final.append(main + ".vtx")

            if any(sub in path for sub in ("sniper", "soldier", "engineer", "scout")): # Check if filepath belongs to model used for one of mentioned classes
                if is_phy_bodygroup and replace_bodygroups:
                    cosmetic_paths_final.extend([main + ".mdl", main + ".vvd", main + ".phy"])

    for path in cosmetic_paths_final: # Create file from each filepath
        cosmetic_folder = (Path(mod_folder) / path).parent
        cosmetic_folder.mkdir(exist_ok=True, parents=True)
        main, ext = os.path.splitext(path)
        tf_class = next((sub for sub in ("sniper", "soldier", "engineer", "scout") if sub in path), None)

        if isinstance(tf_class, str):
            if ext == ".vtx":
                shutil.copy(replacement_folder / (tf_class + ext), str(mod_folder / f"{main}.dx80.vtx"))
                shutil.copy(replacement_folder / (tf_class + ext), str(mod_folder / f"{main}.dx90.vtx"))
                shutil.copy(replacement_folder / (tf_class + ext), str(mod_folder / f"{main}.sw.vtx"))
            elif ext == ".mdl":
                shutil.copy(replacement_folder / (tf_class + ext), str(mod_folder / f"{main}.mdl"))
            elif ext == ".phy" and tf_class != "engineer":
                shutil.copy(replacement_folder / (tf_class + ext), str(mod_folder / f"{main}.phy"))
            elif ext == ".vvd":
                shutil.copy(replacement_folder / (tf_class + ext), str(mod_folder / f"{main}.vvd"))
        elif ext == ".vtx":
            for suffix in ["dx80", "dx90", "sw"]:
                (mod_folder / f"{main}.{suffix}.vtx").write_text("")

    new_vpk = vpk.new(str(mod_folder))
    new_vpk.save("Custom-Cosmetic-Disabler.vpk")
    delete_vpk_folder()

    if os.path.exists("Custom-Cosmetic-Disabler.vpk"): # Check if VPK was created successfully
        vpk_path = os.path.abspath("Custom-Cosmetic-Disabler.vpk")
        messagebox.showinfo("Done", f"VPK file created successfully! Generated at\n{vpk_path}")
    else:
        messagebox.showerror("VPK Failed", "VPK file failed to generate! Please mention this on Github!")


def update_disabled_list(): # Update disabled cosmetics list
    disabled_listbox.delete(0, tk.END)
    # for c in target_cosmetics:
    for c in sorted(target_cosmetics, key=lambda x: x.get("name", "").lower()):
        disabled_listbox.insert(tk.END, c.get("name"))


def load_cosmetics(): # Load all cosmetics from items_game.txt
    global all_cosmetics, all_names
    if not os.path.exists(tf2_dir):
        return
    all_cosmetics = find_cosmetics(os.path.join(tf2_dir, "tf", "scripts", "items", "items_game.txt"))
    #all_names = [c["name"] for c in all_cosmetics if c.get("name")]
    all_names = sorted([c["name"] for c in all_cosmetics if c.get("name")], key=str.lower)
    update_cosmetic_list()


def update_cosmetic_list(*args): # Update enabled cosmetics list
    search_text = search_var.get().lower()
    cosmetic_listbox.delete(0, tk.END)
    for name in all_names:
        if search_text in name.lower():
            cosmetic_listbox.insert(tk.END, name)


# GUI setup
root = tk.Tk()
root.title("TF2 Cosmetic Disabler")
root.geometry("650x600")
icon_path = resource_path(r"tf2_ico.ico")

if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

root.protocol("WM_DELETE_WINDOW", on_close)

# TF2 dir selection
frame_top = ttk.LabelFrame(root, text="TF2 Directory")
frame_top.pack(fill="x", padx=10, pady=5)
ttk.Button(frame_top, text="Select TF2 Folder", command=get_custom_dir).pack(side="left", padx=5, pady=5)
tf2_dir_label = ttk.Label(frame_top, text="No folder selected")
tf2_dir_label.pack(side="left", padx=10)

# Search bar
search_var = tk.StringVar()
search_var.trace_add("write", update_cosmetic_list)
search_frame = ttk.Frame(root)
search_frame.pack(fill="x", padx=10, pady=5)
ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
search_entry = ttk.Entry(search_frame, textvariable=search_var)
search_entry.pack(side="left", fill="x", expand=True)

# Cosmetic list
list_frame = ttk.Frame(root)
list_frame.pack(fill="both", expand=True, padx=10, pady=5)
scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")
cosmetic_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
cosmetic_listbox.pack(fill="both", expand=True)
scrollbar.config(command=cosmetic_listbox.yview)
cosmetic_listbox.bind("<Double-Button-1>", on_all_cosmetics_double_click)

# Disabled cosmetics list
frame_disabled = ttk.LabelFrame(root, text="Disabled Cosmetics")
frame_disabled.pack(fill="both", expand=True, padx=10, pady=5)
disabled_listbox = tk.Listbox(frame_disabled)
disabled_listbox.pack(fill="both", expand=True, padx=5, pady=5)
ttk.Button(frame_disabled, text="Enable Selected", command=lambda: on_disabled_double_click(None)).pack(pady=5)
disabled_listbox.bind("<Double-Button-1>", on_disabled_double_click)

# Bottom buttons
frame_bottom = ttk.Frame(root)
frame_bottom.pack(fill="x", pady=10)
ttk.Button(frame_bottom, text="Save", command=save_cosmetics).pack(side="left", padx=10)
ttk.Button(frame_bottom, text="Create VPK", command=create_vpk).pack(side="left", padx=10)
ttk.Button(frame_bottom, text="Quit", command=on_close).pack(side="right", padx=10)

# Load existing disabled cosmetics
if cosmetic_data.exists():
    with open(cosmetic_data, "r") as f:
        target_cosmetics = json.load(f)
    update_disabled_list()

# Load TF2 folder if previously saved
custom_tf2_file = program_data / "data"
if custom_tf2_file.exists():
    with open(custom_tf2_file, "r") as f:
        saved_dir = f.readline().strip()
    if os.path.exists(os.path.join(saved_dir, "tf", "scripts", "items", "items_game.txt")):
        tf2_dir = saved_dir
        tf2_dir_label.config(text=tf2_dir)
        load_cosmetics()

root.mainloop()