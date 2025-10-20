# // LICENSE FOR VALVE_PARSERS LIBRARY //

# Copyright (c) 2025 valve-parsers contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# // LICENSE FOR TKINTER LIBRARY //

# Copyright (c) 2021, Parth Jadhav
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import sys
import ctypes
from json import JSONDecodeError
from parser import find_cosmetics
from valve_parsers import VPKFile
from concurrent.futures import ThreadPoolExecutor
import json
import shutil
import atexit
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import threading
import requests
from packaging import version
import webbrowser
# Variables & paths

CURRENT_VERSION = "1.1.1"
REPO = "dilbertron2/Cosmetic-Disabler"

items_game_path = Path(r"tf\scripts\items\items_game.txt")
tf2_default_dir = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2")
tf2_dir = Path("")
tf2_misc_dir = Path(r"tf\tf2_misc_dir.vpk")
target_cosmetics = []
all_cosmetics = []
all_names = []
bodygroups_to_replace = {"hat", "headphones", "hands", "shoes", "shoes_socks", "head", "whole_head", "backpack", "dogtags", "grenades", "bullets"}
bodygroups_to_always_replace = {"hands", "shoes_socks", "shoes", "head", "whole_head", "backpack", "grenades", "bullets"}
tf_classes = {"sniper", "soldier", "engineer", "scout", "demo", "heavy", "medic", "pyro", "spy"}
replacement_file_cache = {}
user_is_quitting = False

mod_folder = Path().absolute() / "Cosmetic-Mod-Staging"
program_data = Path().absolute() / "Cosmetic Disabler Data"
cosmetic_data = program_data / "data2"
replacement_folder = Path().absolute() / "Replacement Files"
zombie_skins = replacement_folder / "zombie_skins/materials/models/player"

for folder in (mod_folder, program_data):
    folder.mkdir(exist_ok=True)

if not replacement_folder.exists():
    messagebox.showerror("Missing Folder", f"Replacement model files not found.\nFolder missing at: {replacement_folder}\nThis Software will not work. Please re-download this program from Github or move 'Replacement Files' to the correct location.")

if sys.platform == "win32":  # Force custom app ID to ensure program icon usage
    app_id = u"TF2CosmeticDisabler.app"
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

# Functions
def get_latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(url, timeout=3)
    if response.status_code == 200:
        data = response.json()
        return data["tag_name"].lstrip("v")

def check_for_update():
    try:
        latest = get_latest_release(REPO)
        if version.parse(latest) > version.parse(CURRENT_VERSION):
            answer = messagebox.askyesno("New Version Available!", "A new version of the Cosmetic Disabler is available!\n\nWould you like to go to the download page?")
            if answer:
                webbrowser.open(f"https://gamebanana.com/tools/20969")
    except Exception as e:
        print(f"Could not check for updates: {e}")

def copy_file(src, dst):
    shutil.copy(src, dst)

def write_empty_vtx(path):
    path.write_text("1")

def replacement_exists_cached(path):
    if path not in replacement_file_cache:
        replacement_file_cache[path] = path.exists()

    return replacement_file_cache[path]

def resource_path(relative_path): # Check whether program has been compiled with pyinstaller or is simply running from a straight .py file
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        #base_path = os.path.abspath(".")
        base_path = Path(".").resolve()
    return base_path / relative_path

def delete_vpk_folder():
    if mod_folder.exists():
        shutil.rmtree(mod_folder)


atexit.register(delete_vpk_folder) # Delete VPK staging folder upon program termination


def save_cosmetics(): # Save disabled cosmetics to file
    with open(cosmetic_data, "w") as file:
        json.dump(target_cosmetics, file)
        messagebox.showinfo("Saved", "Disabled cosmetics saved successfully.")


def on_close(): # Prompt save when user wants to quit program
    global user_is_quitting
    if messagebox.askyesno("Saving", "Do you want to save before quitting?"):
        user_is_quitting = True
        save_cosmetics()
        root.destroy()
        delete_vpk_folder()
        return
    user_is_quitting = True
    delete_vpk_folder()
    root.destroy()


def get_custom_dir(): # Prompt user for custom TF2 directory
    global tf2_dir, tf2_misc_dir
    user_folder = Path(filedialog.askdirectory(title="Select Team Fortress 2 folder"))

    if not user_folder:
        return
    if (user_folder / items_game_path).exists():
        tf2_dir = user_folder

        if (tf2_dir / tf2_misc_dir).exists():
            tf2_misc_dir = str(tf2_dir / tf2_misc_dir)

        with open(program_data / "data", "w") as file:
            tf2_dir_str = str(tf2_dir)
            file.write(tf2_dir_str)
        messagebox.showinfo("TF2 Folder Set", f"TF2 directory set to:\n{tf2_dir}")
        tf2_dir_label.config(text=tf2_dir_str)
        load_cosmetics()
    else:
        messagebox.showerror("Error", "Invalid TF2 directory. 'tf.exe' not found!")


def disable_selected(): # Run when cosmetic in enabled list is interacted with
    selections = cosmetic_listbox.curselection()
    if not selections:
        return

    selected_names = {cosmetic_listbox.get(i) for i in selections}
    existing_names = {cosmetic["name"] for cosmetic in target_cosmetics}

    new_cosmetics = [cosmetic for cosmetic in all_cosmetics if cosmetic.get("name") in selected_names and cosmetic.get("name") not in existing_names]

    if not new_cosmetics:
        return

    target_cosmetics.extend(new_cosmetics)

    update_disabled_list()


def enable_selected(): # Run when cosmetic in disabled list is interacted with
    selections = disabled_listbox.curselection()
    if not selections:
        return

    selected_names = {disabled_listbox.get(i) for i in selections}

    global target_cosmetics
    target_cosmetics = [cosmetic for cosmetic in target_cosmetics if cosmetic.get("name") not in selected_names]

    update_disabled_list()


def create_vpk(): # Process disabled cosmetic filepaths and create VPK file
    cosmetic_info_final = {}
    zombie_skin_detected = False
    created_dirs = set() # We cache all created directories to reduce disk I/O
    paths_to_copy = [] # We will batch copy all replacement files to reduce disk I/O
    empty_vtx_paths = []  # We will batch create all empty vtx files to reduce disk I/O
    replace_bodygroups = messagebox.askyesno("Bodygroup Replacements",
                                             "Do you want to replace cosmetic models with stock models when applicable? (Soldier helmet, Sniper hat, etc)\n\nPros:\n\n* Players wearing a disabled cosmetic that affects the hat bodygroup will be wearing the default headwear instead of nothing.\n\nCons:\n\n* If a player wears multiple cosmetics and atleast one of them replaces the default headwear, models have a chance to clip and look ugly.\n\n* A disabled cosmetic replacing Engineer's hard hat will cause the hard hat to have weird physics upon death.")

    # GET BODYGROUPS AND PATHS FOR EVERY COSMETIC
    for cosmetic in target_cosmetics:
        if user_is_quitting:
            return

        cosmetic_paths_final = []

        #Getting cosmetic info

        #paths = cosmetic.get("paths", [])
        paths = [Path(path) for path in cosmetic.get("paths", [])]

        bodygroups = cosmetic.get("bodygroups", [])
        is_phy_bodygroup = cosmetic.get("phy_bodygroup", False)
        name = cosmetic.get("name", "").lower()

        for path in paths:
            # if path in cosmetic_paths_final:
            #     continue

            #path = Path(path)
            #print(path)
            main, ext = path.with_suffix(''), path.suffix

            if ext == ".vtx":
                cosmetic_paths_final.append(path)

            if replace_bodygroups:
                if ext == ".mdl":
                    cosmetic_paths_final.append(path)
                elif ext == ".vvd":
                    cosmetic_paths_final.append(path)

                if is_phy_bodygroup and ext == ".phy": # If cosmetic replaces default headgear
                    cosmetic_paths_final.append(path)
            else: # If cosmetic replaces bodyparts then replace model anyway no matter what
                if any(bodygroup in bodygroups_to_always_replace for bodygroup in bodygroups):
                    if ext == ".mdl":
                        cosmetic_paths_final.append(path)
                    elif ext == ".vvd":
                        cosmetic_paths_final.append(path)


            cosmetic_info_final[name] = {"paths": cosmetic_paths_final, "bodygroups": bodygroups, "name": name}


    #CREATE VPK FOLDER STRUCTURE BASED OFF OF THE PATHS
    for _, cosmetic in cosmetic_info_final.items():
        if user_is_quitting:
            return

        paths = cosmetic.get("paths", [])
        bodygroups = cosmetic.get("bodygroups", [])
        name = cosmetic.get("name", "")
        print(name)

        for path in paths:
            cosmetic_folder = (mod_folder / path).parent
            path = Path(path) # Convert path string to Path object
            if cosmetic_folder not in created_dirs:
                #cosmetic_folder.mkdir(exist_ok=True, parents=True)
                created_dirs.add(cosmetic_folder)

            main, ext, filename = path.with_suffix(''), path.suffix, path.stem

            if "all_class" in str(main): # If the cosmetic is all_class, check for class in last word of filename instead
                tf_class = next((sub for sub in tf_classes if sub in str(filename.split("_")[-1])), None)
                if not tf_class:
                    tf_class = "all_class_one_model"
            else:
                tf_class = next((sub for sub in tf_classes if sub in str(path)), None)
            replacement_model_type = next((bg for bg in bodygroups_to_replace if bg in bodygroups), None)

            if "voodoo-cursed" in name: # Check if cosmetic is a zombie skin
                replacement_model_type = "zombie"


            if isinstance(tf_class, str):
                if tf_class == "scout":  # Enforcing valid bodygroup for Scout
                    if replacement_model_type == "shoes":

                        replacement_model_type = "shoes_socks"
                    elif replacement_model_type == "hat" or replacement_model_type == "headphones":
                        if "hat" in bodygroups and "headphones" in bodygroups:
                            replacement_model_type = "hat_headphones"

                    elif replacement_model_type == "head" or replacement_model_type == "whole_head":
                        if "whole_head" in bodygroups and "headphones" in bodygroups:
                            replacement_model_type = "hat_headphones"

                if replacement_model_type == "hat":
                    if "hat" in bodygroups and ("head" in bodygroups or "whole_head" in bodygroups):
                        replacement_model_type = "head"

                    if "hat" in bodygroups and "shoes" in bodygroups:
                        replacement_model_type = "shoes"

                elif replacement_model_type == "headphones": # Enforce correct bodygroup for multi-class cosmetics that can be worn by scout
                    if "hat" in bodygroups and "headphones" in bodygroups and tf_class != "scout":
                        replacement_model_type = "hat"

                    elif any(name in cosmetic.get("name", "").lower() for name in ("arkham cowl", "promo arkham cowl")):
                        replacement_model_type = "hat"

                        if tf_class == "scout":
                            replacement_model_type = "hat_headphones"

                elif replacement_model_type == "shoes_socks" and tf_class != "scout":
                    replacement_model_type = "shoes"


                target_file = replacement_folder / (tf_class + '_' + str(replacement_model_type) + ext)
                #print(target_file)
                #if target_file.exists(): # Check if current filepath has a valid replacement file
                if replacement_exists_cached(target_file):
                    if ext == ".vtx":
                        if replace_bodygroups or any(bg in bodygroups_to_always_replace for bg in bodygroups):
                            for suffix in ["dx80", "dx90", "sw"]:
                                #shutil.copy(target_file, mod_folder / f"{main}.{suffix}{ext}")
                                paths_to_copy.append((target_file, mod_folder / f"{main}.{suffix}{ext}"))
                        else:
                            for suffix in ["dx80", "dx90", "sw"]:
                                empty_vtx_paths.append(mod_folder / f"{main}.{suffix}{ext}")

                    elif ext == ".mdl" or ext == ".vvd":
                        #shutil.copy(target_file, mod_folder / f"{main}{ext}")
                        paths_to_copy.append((target_file, mod_folder / f"{main}{ext}"))

                    #elif ext == ".phy" and any(bg in ("hat", "headphones") for bg in bodygroups):
                    elif ext == ".phy":
                        #shutil.copy(target_file, mod_folder / f"{main}{ext}")
                        paths_to_copy.append((target_file, mod_folder / f"{main}{ext}"))

                else:
                    if ext == ".vtx":
                        for suffix in ["dx80", "dx90", "sw"]:
                            empty_vtx_paths.append(mod_folder / f"{main}.{suffix}{ext}")

                    if replacement_model_type == "zombie":
                        zombie_skin_detected = True
                        if tf_class == "heavy":
                            tf_class = "hvyweapon"

                        for folder in zombie_skins.iterdir():
                            if folder.is_dir() and folder.name == tf_class:
                                files = [f for f in folder.iterdir() if f.is_file()]
                                for file in files:
                                    ext, filename = file.suffix, file.stem
                                    create_folder = f"materials/models/player/{tf_class}"
                                    (mod_folder / create_folder).mkdir(parents=True, exist_ok=True)
                                    shutil.copy(file, mod_folder / f"materials/models/player/{tf_class}/{filename}{ext}")

    # Batch writing data to disk
    for folder in created_dirs:
        folder.mkdir(parents=True, exist_ok=True)

    # for file, path in paths_to_copy:
    #     shutil.copy(file, path)
    #
    # for vtx_path in empty_vtx_paths:
    #     vtx_path.parent.mkdir(parents=True, exist_ok=True)
    #     vtx_path.write_text("1")

    with ThreadPoolExecutor(max_workers=8) as executor: # Multithreaded file creation
        future_copy = executor.submit(lambda: list(map(lambda args: copy_file(*args), paths_to_copy)))
        future_vtx = executor.submit(lambda: list(map(write_empty_vtx, empty_vtx_paths)))

        future_copy.result()
        future_vtx.result()


    if Path("./Custom-Cosmetic-Disabler.vpk").exists(): # Delete old VPK from previous generation if it exists
        Path("./Custom-Cosmetic-Disabler.vpk").unlink()

    quit_button.config(state="disabled")
    VPKFile.create(str(mod_folder), "Custom-Cosmetic-Disabler.vpk")
    delete_vpk_folder()
    quit_button.config(state="normal")
    if Path("./Custom-Cosmetic-Disabler.vpk").exists(): # Check if VPK was created successfully
        vpk_path = Path("./Custom-Cosmetic-Disabler.vpk").resolve()
        messagebox.showinfo("Done", f"VPK file created successfully! Generated at\n{vpk_path}")
        if zombie_skin_detected:
            messagebox.showwarning("WARNING", "You have disabled atleast one voodoo soul cosmetic.\n\nIn order for them to be disabled correctly in sv_pure 1/2 servers (and Casual) you will have to use Cukei's Casual Preloader.\n\n NOT doing so risks errors/crashes!")
    else:
        messagebox.showerror("VPK Failed", "VPK file failed to generate! Have you disabled atleast one cosmetic?")

def start_vpk_creation():
    create_vpk_button.config(state="disabled", text="Creating VPK.. Please Wait")

    def task():
        try:
            create_vpk()
        finally:
            root.after(0, lambda: create_vpk_button.config(state="normal", text="Create VPK"))

    threading.Thread(target=task, daemon=True).start()

def load_cosmetics(): # Load all cosmetics from items_game.txt
    global all_cosmetics, all_names
    #if not os.path.exists(tf2_dir):
    if not tf2_dir.exists():
        return
    #all_cosmetics = find_cosmetics(os.path.join(tf2_dir, "tf", "scripts", "items", "items_game.txt"))
    all_cosmetics = find_cosmetics((tf2_dir / items_game_path), tf2_misc_dir)
    #all_names = [c["name"] for c in all_cosmetics if c.get("name")]
    all_names = sorted([c["name"] for c in all_cosmetics if c.get("name")], key=str.lower)
    update_cosmetic_list()


def disable_all_cosmetics():
    answer = messagebox.askyesno("Disable All Cosmetics", f"Are you sure you want to disable EVERY cosmetic?")
    if answer:
        existing = {cosmetic["name"] for cosmetic in target_cosmetics}
        for cosmetic in all_cosmetics:
            #if not cosmetic in target_cosmetics:
            if cosmetic["name"] not in existing:
                target_cosmetics.append(cosmetic)

        update_disabled_list()


def update_cosmetic_list(*args): # Update enabled cosmetics list
    search_text = search_var.get().lower()
    cosmetic_listbox.delete(0, tk.END)
    for name in all_names:
        if search_text in name.lower():
            cosmetic_listbox.insert(tk.END, name)


def update_disabled_list(*args): # Update disabled cosmetics list
    search_text = search_var_disabled.get().lower()
    disabled_listbox.delete(0, tk.END)
    # for c in target_cosmetics:
    for cosmetic in sorted(target_cosmetics, key=lambda x: x.get("name", "").lower()):
        name = cosmetic.get("name", "")
        if search_text in name.lower():
            disabled_listbox.insert(tk.END, name)

def update_disabled_list_no_search(*args): # Update disabled cosmetics list without search check
    disabled_listbox.delete(0, tk.END)
    # for c in target_cosmetics:
    for cosmetic in sorted(target_cosmetics, key=lambda x: x.get("name", "").lower()):
        name = cosmetic.get("name", "")
        disabled_listbox.insert(tk.END, name)

def clear_target_cosmetics():
    global target_cosmetics
    answer = messagebox.askyesno("Clear Disabled Cosmetics", f"Are you sure you want to clear your disabled cosmetics?")
    if answer:
        target_cosmetics = []
        update_disabled_list_no_search()

# GUI setup
root = tk.Tk()
root.title("TF2 Cosmetic Disabler")
root.geometry("650x600")
icon_path = resource_path(r"tf2_ico.ico")

if Path(icon_path).exists():
    root.iconbitmap(icon_path)
root.protocol("WM_DELETE_WINDOW", on_close)

# Menu bar
# menubar = Menu(root)
# cosmetics_menu = Menu(menubar, tearoff=0)
# cosmetics_menu.add_command(label="Import Cosmetic List", command=disable_all_cosmetics)
# cosmetics_menu.add_command(label="Export Cosmetic List", command=clear_target_cosmetics)
# menubar.add_cascade(label="Cosmetics", menu=cosmetics_menu)
#
# spacer = tk.Frame(root, height=6, bg="#f0f0f0")  # same color as default background
# spacer.pack(fill="x")
#
# root.config(menu=menubar)

# TF2 dir selection
frame_top = ttk.Frame(root)
frame_top.pack(fill="x")
ttk.Button(frame_top, text="Select TF2 Folder", command=get_custom_dir).pack(side="left", padx=5, pady=5)
tf2_dir_label = ttk.Label(frame_top, text="No folder selected")
tf2_dir_label.pack(side="left", padx=10)

frame_general = ttk.LabelFrame(root, text="Cosmetics")
frame_general.pack(fill="both", expand=True, padx=10, pady=5)

# Search bar
search_var = tk.StringVar()
search_var.trace_add("write", update_cosmetic_list)
search_frame = ttk.Frame(frame_general)
search_frame.pack(fill="x", padx=10, pady=5)
ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
search_entry.pack(side="left")

# Disable Selected Button
ttk.Button(search_frame, text="Disable Selected", command=lambda: disable_selected()).pack(side="left", padx=5)

# Disable All Button
ttk.Button(search_frame, text="Disable All Cosmetics", command=disable_all_cosmetics).pack(side="right", padx=5)

# Cosmetic list
list_frame = ttk.Frame(frame_general)
list_frame.pack(fill="both", expand=True, padx=10, pady=5)
scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")
cosmetic_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.EXTENDED)
cosmetic_listbox.pack(fill="both", expand=True)
scrollbar.config(command=cosmetic_listbox.yview)

# Disabled cosmetics list
frame_disabled = ttk.LabelFrame(root, text="Disabled Cosmetics")
frame_disabled.pack(fill="both", expand=True, padx=10, pady=5)

# Search bar for disabled cosmetics
search_var_disabled = tk.StringVar()
search_var_disabled.trace_add("write", update_disabled_list)
search_frame_disabled = ttk.Frame(frame_disabled)
search_frame_disabled.pack(fill="x", padx=10, pady=5)
ttk.Label(search_frame_disabled, text="Search:").pack(side="left", padx=(0, 5))
search_entry_disabled = ttk.Entry(search_frame_disabled, textvariable=search_var_disabled, width=30)
search_entry_disabled.pack(side="left")

scrollbar2 = ttk.Scrollbar(frame_disabled, orient="vertical")
scrollbar2.pack(side="right", fill="y")

ttk.Button(search_frame_disabled, text="Enable Selected", command=lambda: enable_selected()).pack(side="left", padx=5)

ttk.Button(search_frame_disabled, text="Clear Disabled Cosmetics", command=clear_target_cosmetics).pack(side="right", padx=5)

# Actual disabled cosmetics list
disabled_listbox = tk.Listbox(frame_disabled, yscrollcommand=scrollbar2.set, selectmode=tk.EXTENDED)
disabled_listbox.pack(fill="both", expand=True, padx=5, pady=5)
scrollbar2.config(command=disabled_listbox.yview)

# Bottom buttons
frame_bottom = ttk.Frame(root)
frame_bottom.pack(fill="x", pady=10)
ttk.Button(frame_bottom, text="Save", command=save_cosmetics).pack(side="left", padx=10)
create_vpk_button = ttk.Button(frame_bottom, text="Create VPK", command=start_vpk_creation)
create_vpk_button.pack(side="left", padx=10)
quit_button = ttk.Button(frame_bottom, text="Quit", command=on_close)
quit_button.pack(side="right", padx=10)

# Load existing disabled cosmetics
if cosmetic_data.exists():
    with open(cosmetic_data, "r") as f:
        try:
            target_cosmetics = json.load(f)
        except JSONDecodeError:
            target_cosmetics = []

    update_disabled_list()

# Load TF2 folder if previously saved
custom_tf2_file = program_data / "data"
if custom_tf2_file.exists():
    with open(custom_tf2_file, "r") as f:
        saved_dir = Path(f.readline().strip())
    #if os.path.exists(os.path.join(saved_dir, "tf", "scripts", "items", "items_game.txt")):
    if (saved_dir / items_game_path).exists():
        tf2_dir = saved_dir
        tf2_dir_label.config(text=str(tf2_dir))
        load_cosmetics()

check_for_update()
root.mainloop()