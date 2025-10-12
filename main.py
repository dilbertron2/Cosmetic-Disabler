import os
import vpk
import shutil
from pathlib import Path


tf2_default_dir = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2"
tf2_dir = r""
paths_txt = "paths.txt"
cosmetic_paths = []
mod_folder = Path().absolute() / "Cosmetic-Mod-Staging"
program_data = Path().absolute() / "Cosmetic Disabler Data"

if not mod_folder.exists():
    mod_folder.mkdir()

if not program_data.exists():
    program_data.mkdir()

def get_custom_dir(): # Get custom TF2 location as provided by user.
    print(r"Enter the full path of your TF2 installation. (..steamapps\common\Team Fortress 2)")
    user_input_dir = input("> ")
    if os.path.exists(user_input_dir + r"\tf\scripts\items\items_game.txt"):
        tf2_dir = user_input_dir
        if program_data.exists():
            with open(str(program_data) + r"\data", "w") as file:
                file.write(str(tf2_dir))

    else:
        print(r"Invalid! 'tf\scripts\items\items_game.txt' NOT found. Are you sure the path you provided is correct?")
        get_custom_dir()

def get_user_hat():
    print("What cosmetic would you like to remove? Paste cosmetic file name.")
    user_hat_name = input("> ").lower()
    with open(paths_txt) as file:
        for line in file:
            if user_hat_name in line:
                cosmetic_paths.append(line.replace("\n",""))
    print(cosmetic_paths)

def create_vpk(): # Create the final VPK file for use in TF2, as well as saving all affected cosmetic paths to a file.
    for cosmetic in cosmetic_paths:
        cosmetic_file = Path(mod_folder) / cosmetic
        if not cosmetic_file.exists():
            cosmetic_file.parent.mkdir(exist_ok=True, parents=True)
        with open(cosmetic_file, 'w') as file:
            file.write("")

    new_vpk = vpk.new(str(mod_folder))
    new_vpk.save("Custom-Cosmetic-Disabler.vpk")
    models_folder = mod_folder / "models"
    shutil.rmtree(models_folder)
    with open(disabled_cosmetics_file, 'w') as file:
        for filepath in cosmetic_paths:
            file.write(filepath + "\n")


def main_loop(): # Give the user a choice on what to do
    print("(D)isable a Cosmetic")
    print("(E)nable a Cosmetic")
    print("(L)ist disabled Cosmetics")
    print("(C)reate VPK file")
    print("(Q)uit")
    user_input = input("> ").upper()
    if user_input == "":
        main_loop()
    else:
        if user_input[0] == "D":
            get_user_hat()
            main_loop()
        elif user_input[0] == "C":
            create_vpk()
            main_loop()
        elif user_input[0] == "Q":
            quit()
        elif user_input[0] == "E":
            print("WIP")
            #code re-enabling cosmetics
        elif user_input[0] == "L":
            print("WIP")
            #code listing all disabled cosmetics

custom_tf2_file = program_data / "data" # Check for a custom saved TF2 location and run accordingly.
custom_tf2_location = ""
if custom_tf2_file.exists():
    with open(str(custom_tf2_file), "r") as file:
        custom_tf2_location = file.readline()
    if os.path.exists(custom_tf2_location + r"\tf\scripts\items\items_game.txt"):

        print("TF2 Location detected as " + custom_tf2_location)
        print("Is this correct? Y/N")
        user_input = input("> ").upper()
        if user_input == "N" or user_input == "NO":
            get_custom_dir()

elif not custom_tf2_file.exists():
    if os.path.exists(tf2_default_dir):
        print("TF2 install location auto-detected as: " + tf2_default_dir)
        print("Is this correct? Y/N")
        user_input = input("> ").upper()
        if user_input == "N" or user_input == "NO":
            get_custom_dir()

    elif not os.path.exists(tf2_default_dir):
        get_custom_dir()

disabled_cosmetics_file = program_data / "data2" # Check for already disabled cosmetics and load them.
if disabled_cosmetics_file.exists():
    with open(str(disabled_cosmetics_file), "r") as file:
        for line in file:
            cosmetic_paths.append(line.replace("\n",""))
    print(cosmetic_paths)

print("Cosmetic Disabler Running.. What would you like to do?")
main_loop()