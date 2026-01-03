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

# pyinstaller command lol (remember to provide the "Replacement Files" directory aswell as database.csv with every release)
# pyinstaller --onefile --noconsole --icon "tf2_ico.ico" --add-data "16x16.png;." --add-data "32x32.png;." --add-data "tf2_ico.ico;." "cosmetic_disabler.py"


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
from tkinter import ttk, filedialog, messagebox
import threading
import requests
from packaging import version
import webbrowser
import csv

# Variables & paths

CURRENT_VERSION = "1.2.0"
REPO = "dilbertron2/Cosmetic-Disabler"

tf2_updates = ["Sniper vs. Spy Update", "Classless Update", "Haunted Hallowe'en Special",
               "First Community Contribution Update", "Second Community Contribution Update",
               "Mac Update", "Mann-Conomy Update", "Scream Fortress Update", "Australian Christmas",
               "Shogun Pack", "Japan Charity Bundle", "Third Community Contribution Update",
               "Replay Update", "Über Update", "Summer Camp Sale", "Dr. Grordbort's Victory Pack Update",
               "Manno-Technology Bundle", "Manniversary Update & Sale", "Very Scary Halloween Special",
               "Australian Christmas 2011", "Pyromania Update", "Triad Pack", "Mann vs. Machine Update",
               "First Workshop Content Pack", "Spectral Halloween Special", "Mecha Update", "Robotic Boogaloo",
               "Second Workshop Content Pack", "Summer Event 2013", "Fall Event 2013", "Scream Fortress 2013",
               "Two Cities Update", "Smissmas 2013", "Strongbox Pack", "Love & War Update", "Limited Late Summer Pack",
               "Scream Fortress 2014", "End of the Line Update", "Smissmas 2014", "Gun Mettle Update", "Invasion Community Update",
               "Scream Fortress 2015", "Tough Break Update", "Mayflower Pack", "Meet Your Match Update", "Scream Fortress 2016",
               "Smissmas 2016", "Rainy Day Pack", "Jungle Inferno Update", "Smissmas 2017", "Blue Moon Pack", "Scream Fortress 2018",
               "Smissmas 2018", "Summer 2019 Pack", "Scream Fortress 2019", "Smissmas 2019", "Summer 2020 Pack", "Scream Fortress 2020",
               "Smissmas 2020", "Summer 2021 Pack", "Scream Fortress 2021", "Smissmas 2021", "Summer 2022 Pack", "Scream Fortress 2022",
               "Smissmas 2022", "Summer 2023 Pack", "Scream Fortress 2023", "Smissmas 2023", "Summer 2024 Pack", "Scream Fortress 2024",
               "Smissmas 2024", "Summer 2025 Pack", "Scream Fortress 2025", "Smissmas 2025"]
engy_cosmetics = ["antlers", "merc's muffler"]

items_game_path = Path("tf/scripts/items/items_game.txt")
tf2_dir = Path("")
tf2_misc_dir = Path("tf/tf2_misc_dir.vpk")
target_cosmetics = []
target_cosmetic_names = []
all_cosmetics = []
all_names = []
all_names_by_date = []
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
update_db = Path().absolute() / "database.csv"
update_db_contents = None

for folder in (mod_folder, program_data):
    folder.mkdir(exist_ok=True)

if not replacement_folder.exists():
    messagebox.showerror("Missing Folder", f"Replacement model files not found.\nFolder missing at: {replacement_folder}\nThis Software will not work. Please re-download this program from Github or move 'Replacement Files' to the correct location.")

if sys.platform == "win32":  # Force custom app ID to ensure program icon usage
    app_id = u"TF2CosmeticDisabler.app"
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception as e:
        print(e)
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
        latest_version = version.parse(latest)
        current_version = version.parse(CURRENT_VERSION)
        if latest_version > current_version:
            answer = messagebox.askyesno("New Version Available!", f"A new version of the Cosmetic Disabler is available!\n\nWould you like to go to the download page?\n\nCurrent Version: {current_version}\nLatest Version: {latest_version}")
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
        base_path = Path(".").resolve()
    return base_path / relative_path

def auto_detect_tf2():
    # Attempt to automatically detect TF2 installation directory from common locations (linux and windows)
    common_paths = [
        "C:/Program Files (x86)/Steam/steamapps/common/Team Fortress 2",
        "D:/Program Files (x86)/Steam/steamapps/common/Team Fortress 2",
        "~/.steam/steam/steamapps/common/Team Fortress 2",
        "~/.local/share/Steam/steamapps/common/Team Fortress 2",
    ]

    for path_str in common_paths:
        path = Path(path_str).expanduser()
        if path.exists() and (path / items_game_path).exists():
            return path

    return None

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
        messagebox.showerror("Error", "Invalid TF2 directory. 'tf/scripts/items/items_game.txt' not found!")

def update_target_cosmetic_name_list():
    global target_cosmetic_names

    target_cosmetic_names.clear()

    for cosmetic in target_cosmetics:
        name = cosmetic.get("name", "")
        if name:
            target_cosmetic_names.append(name)


def disable_selected(): # Run when 'Disable Selected' is activated
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


def enable_selected(): # Run when 'Enable Selected' is activated
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
        paths = [Path(path) for path in cosmetic.get("paths", [])]

        bodygroups = cosmetic.get("bodygroups", [])
        is_phy_bodygroup = cosmetic.get("phy_bodygroup", False)
        name = cosmetic.get("name", "").lower()

        for path in paths:
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

        # This is where we do the HORRIBLE hard-coded behaviour for fucky cosmetics
        if name == "grandmaster" and paths:
            for path in paths:
                filename = path.stem
                last_word = filename.split("_")[-1]
                if last_word == "red":
                    new_path = path.with_name(path.name.replace("red", "blue"))
                    paths.append(new_path)


        for path in paths:
            print(f"START OF VPK CREATION: {path}")
            cosmetic_folder = (mod_folder / path).parent
            path = Path(path) # Convert path string to Path object
            if cosmetic_folder not in created_dirs:
                #cosmetic_folder.mkdir(exist_ok=True, parents=True)
                created_dirs.add(cosmetic_folder)

            main, ext, filename = path.with_suffix(''), path.suffix, path.stem

            # Let's modify main if current cosmetic has stupid internal filename
            if name in engy_cosmetics:
                parent = main.parent
                new_filename = main.stem.replace("engineer", "engy")
                new_path = parent / f"{new_filename}"
                main = new_path

            filename_parts = filename.split("_")

            if "all_class" in str(main): # If the cosmetic is all_class, check for class in last word of filename instead
                #tf_class = next((sub for sub in tf_classes if sub in str(filename.split("_"))[-1]), None)
                if filename_parts:
                    tf_class = next((sub for sub in tf_classes if sub in filename_parts[-1]), None)
                    if not tf_class:
                        if len(filename_parts) >= 2:
                            tf_class = next((sub for sub in tf_classes if sub in filename_parts[-2]), None) # If for some reason class isn't last word in name, check second to last
                            if not tf_class:
                                tf_class = next((sub for sub in tf_classes if sub in filename_parts[0]), None) # Check first word
                if not tf_class:
                    tf_class = "all_class_one_model"
            else:
                tf_class = next((sub for sub in tf_classes if sub in str(path)), None)
            replacement_model_type = next((bg for bg in bodygroups_to_replace if bg in bodygroups), None)

            if "voodoo-cursed" in name: # Check if cosmetic is a zombie skin
                replacement_model_type = "zombie"

            if isinstance(tf_class, str): # Replacement model type check
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


                if replacement_exists_cached(target_file):
                    if ext == ".vtx":
                        if replace_bodygroups or any(bg in bodygroups_to_always_replace for bg in bodygroups):
                            for suffix in ["dx80", "dx90", "sw"]:
                                paths_to_copy.append((target_file, mod_folder / f"{main}.{suffix}{ext}"))
                        else:
                            for suffix in ["dx80", "dx90", "sw"]:
                                empty_vtx_paths.append(mod_folder / f"{main}.{suffix}{ext}")

                    elif ext == ".mdl" or ext == ".vvd":
                        paths_to_copy.append((target_file, mod_folder / f"{main}{ext}"))

                    #elif ext == ".phy" and any(bg in ("hat", "headphones") for bg in bodygroups):
                    elif ext == ".phy":
                        paths_to_copy.append((target_file, mod_folder / f"{main}{ext}"))

                else:
                    if ext == ".vtx":
                        for suffix in ["dx80", "dx90", "sw"]:
                            empty_vtx_paths.append(mod_folder / f"{main}.{suffix}{ext}")

                    if replacement_model_type == "zombie": # Voodoo souls require material changes
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

    #print(f"paths to copy: {paths_to_copy}")

    # Batch writing data to disk
    for folder in created_dirs:
        folder.mkdir(parents=True, exist_ok=True)

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
        messagebox.showinfo("Done!", f"VPK file created successfully! Generated at\n{vpk_path}\n\nThank you for using this program created by Dilbertron!")
        if zombie_skin_detected:
            messagebox.showwarning("WARNING", "You have disabled atleast one voodoo soul cosmetic.\n\nIn order for them to be disabled correctly in sv_pure 1/2 servers (and Casual) you will have to use a Casual preloader.\n\n NOT doing so risks errors/crashes!")
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
    global all_cosmetics, all_names, all_names_by_date

    if not tf2_dir.exists():
        return

    all_cosmetics = find_cosmetics((tf2_dir / items_game_path), tf2_misc_dir)

    all_names = sorted([c["name"] for c in all_cosmetics if c.get("name")], key=str.lower)
    all_names_by_date = [c["name"] for c in all_cosmetics if c.get("name")]
    #update_cosmetic_list()
    dropdown_box_change()


def disable_all_cosmetics():
    answer = messagebox.askyesno("Disable All Cosmetics", f"Are you sure you want to disable EVERY cosmetic?")
    if answer:
        existing = {cosmetic["name"] for cosmetic in target_cosmetics}
        for cosmetic in all_cosmetics:

            if cosmetic["name"] not in existing:
                target_cosmetics.append(cosmetic)

        update_target_cosmetic_name_list()
        update_disabled_list()



def update_cosmetic_list(*args): # Update enabled cosmetics list whenever search changes OR cosmetics disabled
    search_text = search_var.get().lower()
    search_text2 = search_text.replace("u", "Ü").lower()
    cosmetic_listbox.delete(0, tk.END)
    for name in all_names:
        if search_text in name.lower() or search_text2 in name.lower():
            if not name in target_cosmetic_names:
                cosmetic_listbox.insert(tk.END, name)


def update_disabled_list(*args): # Update disabled cosmetics list
    search_text = search_var_disabled.get().lower()
    search_text2 = search_text.replace("u", "Ü").lower()
    disabled_listbox.delete(0, tk.END)

    for cosmetic in sorted(target_cosmetics, key=lambda x: x.get("name", "").lower()):
        name = cosmetic.get("name", "")
        if search_text in name.lower() or search_text2 in name.lower():
            disabled_listbox.insert(tk.END, name)

    update_target_cosmetic_name_list()
    #update_cosmetic_list()
    dropdown_box_change()

def update_disabled_list_no_search(*args): # Update disabled cosmetics list without search check
    disabled_listbox.delete(0, tk.END)

    for cosmetic in sorted(target_cosmetics, key=lambda x: x.get("name", "").lower()):
        name = cosmetic.get("name", "")
        disabled_listbox.insert(tk.END, name)

def clear_target_cosmetics():
    global target_cosmetics
    answer = messagebox.askyesno("Clear Disabled Cosmetics", f"Are you sure you want to clear your disabled cosmetics?")
    if answer:
        target_cosmetics = []
        update_disabled_list()

def open_window(window: tk.Toplevel):
    window.state("normal")
    window.lift()

def minimise_window(window: tk.Toplevel):
    window.withdraw()

# FUNCTIONS FOR CATEGORISING COSMETICS BY UPDATE
def get_update_db():
    global tf2_updates

    if not update_db.exists():
        tf2_updates = ["database.csv", "not found.", "please place", "the file", "inside of", "this program's", "root folder"]
        return None

    subset_data = []

    with open(update_db, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        for row in reader:
            filtered_entry = {
                'hat': row['hat'],
                'update': row['update']
            }
            subset_data.append(filtered_entry)
    subset_data.pop(0) # Remove placeholder hat from DB

    return subset_data

update_db_contents = get_update_db()

def standardize_update_names(): # The database has some update inconsistencies, lets fix that

    if not update_db.exists():
        return

    update_map = { # Scream Fortress update map
        "Scream Fortress VII": "Scream Fortress 2015",
        "Scream Fortress VIII": "Scream Fortress 2016",
        "Scream Fortress X": "Scream Fortress 2018",
        "Scream Fortress XI": "Scream Fortress 2019",
        "Scream Fortress XII": "Scream Fortress 2020",
        "Scream Fortress XIII": "Scream Fortress 2021",
        "Scream Fortress XIV": "Scream Fortress 2022",
        "Scream Fortress XV": "Scream Fortress 2023",
        "Scream Fortress XVI": "Scream Fortress 2024",
        "Scream Fortress XVII": "Scream Fortress 2025"
    }


    for cosmetic in update_db_contents:
        update = cosmetic.get("update", "")

        if update == "Sniper vs. Spy":
            cosmetic.update({"update":"Sniper vs. Spy Update"})
        elif update == "Invasion Update":
            cosmetic.update({"update":"Invasion Community Update"})
        elif "Ãœ" in update:
            cosmetic.update({"update":update.replace("Ãœ", "Ü")})

        for numeral, full_update in update_map.items(): # Loop for Scream Fortress stuff
            if numeral in update:
                cosmetic.update({"update":full_update})

        name = cosmetic.get("hat", "")

        if "Ãœ" in name: # Fix broken formatting on cosmetics that use "Ü"
            new_name = name.replace("Ãœ", "Ü")
            cosmetic.update({"hat":new_name})


def populate_update_box():
    tf2_updatesvar = tk.StringVar(value=tf2_updates)
    updates_listbox.config(listvariable=tf2_updatesvar)


def get_cosmetics_from_updates():
    cosmetics_in_target_updates = []
    selections = updates_listbox.curselection()
    update_list = [updates_listbox.get(i) for i in selections]

    if isinstance(update_list, list):
        for cosmetic in update_db_contents:
            update = cosmetic.get("update", "no update")
            name = cosmetic.get("hat", "no name").lower()
            if update in update_list:
                cosmetics_in_target_updates.append(name)

    return set(cosmetics_in_target_updates)


def disable_selected_updates(): # Run when 'Disable Selected' is activated
    cosmetics_in_update = get_cosmetics_from_updates()

    # existing_names = [cosmetic["name"] for cosmetic in target_cosmetics]
    existing_names = []

    for cosmetic in target_cosmetics:
        cos_name = cosmetic.get("name", "").lower()
        if cos_name:
            if cos_name in cosmetics_in_update:
                existing_names.append(cos_name)



    new_cosmetics2 = []
    for cosmetic in cosmetics_in_update:

        if cosmetic in existing_names:
            continue

        for target_cosmetic in all_cosmetics:

            target_cos_name = target_cosmetic.get("name", "").lower()
            if cosmetic == target_cos_name:

                new_cosmetics2.append(target_cosmetic)
                break

    target_cosmetics.extend(new_cosmetics2)

    update_disabled_list()


def enable_selected_updates(): # Run when 'Enable Selected' is activated
    global target_cosmetics
    selected_names = get_cosmetics_from_updates()

    target_cosmetics = [cosmetic for cosmetic in target_cosmetics if cosmetic.get("name").lower() not in selected_names]

    update_disabled_list()


def dropdown_box_change(*args):
    try:
        selection = cosmetic_dropdown_selection.get()
        if cosmetic_listbox:
            if selection == "Alphabetical":
                update_cosmetic_list()
            elif selection == "Date":
                search_text = search_var.get().lower()
                search_text2 = search_text.replace("u", "Ü").lower()
                cosmetic_listbox.delete(0, tk.END)
                for name in all_names_by_date:
                    if search_text in name.lower() or search_text2 in name.lower():
                        if not name in target_cosmetic_names:
                            cosmetic_listbox.insert(tk.END, name)

    except NameError:
        print("cosmetic_listbox not initialised, this should only trigger on the first execution")

def disabled_dropdown_box_change(*args):
    try:
        selection = disabled_dropdown_selection.get()
        if disabled_listbox:
            if selection == "Alphabetical":
                update_disabled_list()
            elif selection == "Date":
                search_text = search_var_disabled.get().lower()
                search_text2 = search_text.replace("u", "Ü").lower()
                disabled_listbox.delete(0, tk.END)

                for cos_name in all_names_by_date:
                    if cos_name in target_cosmetic_names:
                        if search_text in cos_name.lower() or search_text2 in cos_name.lower():
                            disabled_listbox.insert(tk.END, cos_name)

                update_target_cosmetic_name_list()
                dropdown_box_change()

    except NameError:
        print("disabled_listbox not initialised, this should only trigger on the first execution")

# GUI setup
root = tk.Tk()
root.title("TF2 Cosmetic Disabler")
root.geometry("670x750")
icon_path = resource_path(r"tf2_ico.ico")
small_png_path = resource_path(r"16x16.png")
big_png_path = resource_path(r"32x32.png")

if Path(icon_path).exists():
    try:
        root.iconbitmap(icon_path)
    except Exception:
        # iconbitmap doesn't work with .ico files on Linux
        try:
            if sys.platform.startswith("linux"):
                if small_png_path.exists() and big_png_path.exists():
                    large_icon = tk.PhotoImage(file = big_png_path)
                    small_icon = tk.PhotoImage(file = small_png_path)
                    root.iconphoto(False, large_icon, small_icon)
        except Exception:
            pass
        pass

root.protocol("WM_DELETE_WINDOW", on_close)


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
search_var.trace_add("write", dropdown_box_change)
search_frame = ttk.Frame(frame_general)
search_frame.pack(fill="x", padx=10, pady=5)
ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
search_entry.pack(side="left")

# Drop-down box
cosmetic_dropdown_selection = tk.StringVar()
cosmetic_dropdown_selection.trace_add("write", dropdown_box_change)
cosmetic_dropdown = ttk.Combobox(search_frame, values=["Alphabetical", "Date"], state="readonly", textvariable=cosmetic_dropdown_selection, width=12)
cosmetic_dropdown.pack(side="left", padx=5)
cosmetic_dropdown_selection.set("Alphabetical")

def list_sorting_help():
    list_sorting_info_button.config(state="disabled")
    disabled_list_sorting_info_button.config(state="disabled")
    messagebox.showinfo("Information", "The date sort is not fully accurate as it simply lists cosmetics as they appear in items_game.txt, plus a few other quirks.\n\nit should be mostly correct though!")
    list_sorting_info_button.config(state="normal")
    disabled_list_sorting_info_button.config(state="normal")

list_sorting_info_button = ttk.Button(search_frame, text="?", command=list_sorting_help, width=3)
list_sorting_info_button.pack(side="left")

# Disable Selected Button
ttk.Button(search_frame, text="Disable Selected", command=lambda: disable_selected()).pack(side="left", padx=5)

# Disable Based On Update

# Window Setup
disable_update_win = tk.Toplevel(root)
disable_update_win.geometry("260x600")
disable_update_win.title("Disable Based On Update")
disable_update_win.protocol("WM_DELETE_WINDOW", lambda: minimise_window(disable_update_win))
minimise_window(disable_update_win)

DU_frame = ttk.Frame(disable_update_win)
DU_frame.pack(fill="both", expand=True, padx=10, pady=5)

DU_scrollbar = ttk.Scrollbar(DU_frame, orient="vertical")
DU_scrollbar.pack(side="right", fill="y")
updates_listbox = tk.Listbox(DU_frame, yscrollcommand=DU_scrollbar.set, selectmode=tk.EXTENDED)
updates_listbox.pack(fill="both", expand=True)
populate_update_box()
DU_scrollbar.config(command=updates_listbox.yview)

DU_button_frame = ttk.Frame(disable_update_win)
DU_button_frame.pack(fill="x", padx=10, pady=5)

DU_button_frame.columnconfigure(0, weight=1)
DU_button_frame.columnconfigure(1, weight=0)
DU_button_frame.columnconfigure(2, weight=1)

def update_modifier_help():
    update_help_button.config(state="disabled")
    messagebox.showinfo("Information", "Select the cosmetic update groups you want to modify, then press the corresponding button!\n\nOnly full/major updates are included, so promo items and cosmetics added in random patches will probably NOT be included in your selected updates, you may have to refine your selections further manually.")
    disable_update_win.lift()
    update_help_button.config(state="normal")

ttk.Button(DU_button_frame, text="Disable", command=lambda: disable_selected_updates()).grid(row=0, column=0, sticky=tk.W)
update_help_button = ttk.Button(DU_button_frame, text="?", command=update_modifier_help, width=5)
update_help_button.grid(row=0, column=1)
ttk.Button(DU_button_frame, text="Enable", command=lambda: enable_selected_updates()).grid(row=0, column=2, sticky=tk.E)

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

# Drop-down box
disabled_dropdown_selection = tk.StringVar()
disabled_dropdown_selection.trace_add("write", disabled_dropdown_box_change)
disabled_dropdown = ttk.Combobox(search_frame_disabled, values=["Alphabetical", "Date"], state="readonly", textvariable=disabled_dropdown_selection, width=12)
disabled_dropdown.pack(side="left", padx=5)
disabled_dropdown_selection.set("Alphabetical")

disabled_list_sorting_info_button = ttk.Button(search_frame_disabled, text="?", command=list_sorting_help, width=3)
disabled_list_sorting_info_button.pack(side="left")

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
ttk.Button(frame_bottom, text="Modify By Update", command=lambda: open_window(disable_update_win)).pack(side="left", padx=10)
#ttk.Button(frame_bottom, text="Import/Export List", command=lambda: open_window(disable_update_win)).pack(side="left", padx=10)
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

    if (saved_dir / items_game_path).exists():
        tf2_dir = saved_dir
        tf2_dir_label.config(text=str(tf2_dir))
        load_cosmetics()
else:
    # Try auto-detection if no saved folder exists
    detected_dir = auto_detect_tf2()
    if detected_dir:
        tf2_dir = detected_dir
        tf2_dir_label.config(text=str(tf2_dir))
        with open(custom_tf2_file, "w") as file:
            file.write(str(tf2_dir))
        load_cosmetics()
        messagebox.showinfo("TF2 Auto-Detected", f"TF2 directory automatically detected at:\n{tf2_dir}")

standardize_update_names()
check_for_update()
root.mainloop()
