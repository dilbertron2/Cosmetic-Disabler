import os
from parser import find_cosmetics
import vpk
import json
import shutil
import atexit
from pathlib import Path

tf2_default_dir = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2"
tf2_dir = r""
target_cosmetics = []
mod_folder = Path().absolute() / "Cosmetic-Mod-Staging"
program_data = Path().absolute() / "Cosmetic Disabler Data"
cosmetic_data = program_data / "data2"
replacement_folder = Path().absolute() / "Replacement Files"

if not mod_folder.exists():
    mod_folder.mkdir()

if not program_data.exists():
    program_data.mkdir()

def delete_vpk_folder():
    if mod_folder.exists():
        shutil.rmtree(mod_folder)

atexit.register(delete_vpk_folder)

def save_cosmetics():
    with open(cosmetic_data, "w") as file:
        json.dump(target_cosmetics, file)

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
    print("What cosmetic would you like to remove? Provide cosmetic name.")
    similar_cosmetics = []
    found_exact_match = False
    user_hat_name = input("> ").strip().lower()

    cosmetics = find_cosmetics(tf2_dir + r"\tf\scripts\items\items_game.txt")

    for cosmetic in cosmetics:
        cosmetic_name = cosmetic.get("name")

        if cosmetic_name and user_hat_name in cosmetic_name and user_hat_name != cosmetic_name:
            similar_cosmetics.append(cosmetic_name)
        if cosmetic_name and cosmetic_name == user_hat_name:
            if cosmetic not in target_cosmetics:
                target_cosmetics.append(cosmetic)
                print(target_cosmetics)

            found_exact_match = True

    if similar_cosmetics and not found_exact_match:
        print("Cosmetic not found. Did you mean one of the following?")
        for name in similar_cosmetics:
            print(f" * {name}")
    elif not found_exact_match:
        print("Cosmetic not found.")


def create_vpk(): # Create the final VPK file for use in TF2, as well as saving all affected cosmetic paths to a file.
    cosmetic_paths_final = []

    for cosmetic in target_cosmetics:
        paths = cosmetic.get("paths")
        is_phy_bodygroup = cosmetic.get("phy_bodygroup")
        for path in paths:
            main, ext = os.path.splitext(path)
            new_path = main + ".vtx"
            cosmetic_paths_final.append(new_path)

            if any(sub in path for sub in ("sniper", "soldier", "engineer", "scout")):
                new_path = main + ".mdl"
                cosmetic_paths_final.append(new_path)

                if is_phy_bodygroup:
                    new_path = main + ".phy"
                    cosmetic_paths_final.append(new_path)

                new_path = main + ".vvd"
                cosmetic_paths_final.append(new_path)

    for path in cosmetic_paths_final:
        cosmetic_folder = (Path(mod_folder) / path).parent

        if not cosmetic_folder.exists():
            cosmetic_folder.mkdir(exist_ok=True, parents=True)

        main, ext = os.path.splitext(path)

        tf_class = next((sub for sub in ("sniper", "soldier", "engineer", "scout") if sub in path), None)

        if isinstance(tf_class, str):  # Check if cosmetic belongs to either sniper, soldier, engineer or scout.
            if ext == ".vtx":
                shutil.copy(replacement_folder / (tf_class + ext), (str(mod_folder.absolute()) + "/" + main) + ".dx80.vtx")
                shutil.copy(replacement_folder / (tf_class + ext), (str(mod_folder.absolute()) + "/" + main) + ".dx90.vtx")
                shutil.copy(replacement_folder / (tf_class + ext), (str(mod_folder.absolute()) + "/" + main) + ".sw.vtx")

            elif ext == ".mdl":
                shutil.copy(replacement_folder / (tf_class + ext), (str(mod_folder.absolute()) + "/" + main) + ".mdl")

            elif ext == ".phy" and tf_class != "engineer":
                shutil.copy(replacement_folder / (tf_class + ext), (str(mod_folder.absolute()) + "/" + main) + ".phy")

            elif ext == ".vvd":
                shutil.copy(replacement_folder / (tf_class + ext), (str(mod_folder.absolute()) + "/" + main) + ".vvd")

        elif not isinstance(tf_class,
                            str) and ext == ".vtx":  # If cosmetic doesn't belong to any of the above classes, execute this instead.
            with open(str(mod_folder.absolute()) + "/" + main + ".dx80.vtx", 'w') as file:
                file.write("")

            with open(str(mod_folder.absolute()) + "/" + main + ".dx90.vtx", 'w') as file:
                file.write("")

            with open(str(mod_folder.absolute()) + "/" + main + ".sw.vtx", 'w') as file:
                file.write("")

    new_vpk = vpk.new(str(mod_folder))
    new_vpk.save("Custom-Cosmetic-Disabler.vpk")
    delete_vpk_folder()

    save_cosmetics()

def enable_cosmetic():
    print("Disabled Cosmetics:")
    print()
    for cosmetic in target_cosmetics:
        cosmetic_name = cosmetic.get("name")
        if cosmetic_name:
            print(f"* {cosmetic_name}")
    print()
    print(f"{len(target_cosmetics)} cosmetics disabled.")
    if len(target_cosmetics) == 0:
        return
    print("Which cosmetic do you want to enable?")

    target_cosmetic_name = input("> ").strip().lower()
    for cosmetic in target_cosmetics:
        cosmetic_name = cosmetic.get("name")

        if cosmetic_name == target_cosmetic_name:
            target_cosmetics.remove(cosmetic)


def list_disabled_cosmetics():
    for cosmetic in target_cosmetics:
        cosmetic_name = cosmetic.get("name")
        print(f"* {cosmetic_name}")
    print()
    print(f"{len(target_cosmetics)} cosmetics disabled.")

def main_loop(): # Give the user a choice on what to do
    print("(C)reate VPK file")
    print("(D)isable a Cosmetic")
    print("(E)nable a Cosmetic")
    print("(L)ist disabled Cosmetics")
    print("(S)ave disabled Cosmetics")
    print("(Q)uit")
    print("NOTICE: Creating a VPK automatically saves your disabled Cosmetics!")
    user_input = input("> ").strip().upper()
    if user_input == "":
        main_loop()
    else:
        while True:
            if user_input[0] == "D":#disable cosmetic
                get_user_hat()
                main_loop()
                break
            elif user_input[0] == "C":#create vpk
                create_vpk()
                main_loop()
                break
            elif user_input[0] == "Q":#quit
                quit()
            elif user_input[0] == "E":#enable cosmetic
                enable_cosmetic()
                main_loop()
                break
            elif user_input[0] == "L":#list disabled cosmetics
                list_disabled_cosmetics()
                main_loop()
                break
            elif user_input[0] == "S":
                save_cosmetics()
                main_loop()
                break
            else:
                main_loop()
                break


custom_tf2_file = program_data / "data" # Check for a custom saved TF2 location and run accordingly.
custom_tf2_location = ""
if custom_tf2_file.exists():
    with open(str(custom_tf2_file), "r") as file:
        custom_tf2_location = file.readline()
    if os.path.exists(custom_tf2_location + r"\tf\scripts\items\items_game.txt"):

        print("TF2 Location detected as " + custom_tf2_location)
        print("Is this correct? Y/N")
        while True:
            user_input = input("> ").strip().upper()

            if user_input in ("N", "NO"):
                get_custom_dir()
                break

            elif user_input in ("Y", "YES"):
                tf2_dir = tf2_default_dir
                break

            else:
                print("Invalid input. Please enter Y/YES or N/NO.")


elif not custom_tf2_file.exists():
    if os.path.exists(tf2_default_dir):
        print("TF2 install location auto-detected as: " + tf2_default_dir)
        print("Is this correct? Y/N")
        while True:
            user_input = input("> ").strip().upper()
            if user_input == "N" or user_input == "NO":
                get_custom_dir()
                break

            elif user_input == "Y" or user_input == "YES":
                tf2_dir = tf2_default_dir
                break
            else:
                print("Invalid input. Please enter Y/YES or N/NO.")

    elif not os.path.exists(tf2_default_dir):
        get_custom_dir()

if cosmetic_data.exists():
    with open(cosmetic_data, "r") as file:
        target_cosmetics = json.load(file)

print("Cosmetic Disabler Running.. What would you like to do?")
main_loop()