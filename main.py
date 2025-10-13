import os
from parser import find_cosmetics
import vpk
import shutil
from pathlib import Path


tf2_default_dir = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2"
tf2_dir = r""
paths_txt = "paths.txt"
cosmetic_names = []
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
    print("What cosmetic would you like to remove? Provide cosmetic name.")
    similar_cosmetics = []
    found_exact_match = False
    user_hat_name = input("> ").strip().lower()
    # with open(paths_txt) as file:
    #     for line in file:
    #         if user_hat_name in line:
    #             cosmetic_paths.append(line.replace("\n",""))

    cosmetics = find_cosmetics(tf2_dir + r"\tf\scripts\items\items_game.txt")

    for cosmetic in cosmetics:
        cosmetic_name = cosmetic.get("name")

        if cosmetic_name and user_hat_name in cosmetic_name and user_hat_name != cosmetic_name:
            similar_cosmetics.append(cosmetic_name)

        if cosmetic_name and cosmetic_name == user_hat_name:
            if cosmetic_name not in cosmetic_names:
                cosmetic_names.append(cosmetic_name)

            found_exact_match = True
            current_cosmetic_paths = cosmetic.get("paths")
            if current_cosmetic_paths:
                for path in current_cosmetic_paths:
                    print(cosmetic_paths)
                    if path not in cosmetic_paths:
                        cosmetic_paths.append(path)

    if similar_cosmetics and not found_exact_match:
        print("Cosmetic not found. Did you mean one of the following?")
        for name in similar_cosmetics:
            print(f" * {name}")
    elif not found_exact_match:
        print("Cosmetic not found.")


def create_vpk(): # Create the final VPK file for use in TF2, as well as saving all affected cosmetic paths to a file.
    cosmetic_paths_final = []

    for path in cosmetic_paths:
        main, ext = os.path.splitext(path)
        new_path = main + ".dx80.vtx"
        new_path2 = main + ".dx90.vtx"
        cosmetic_paths_final.append(new_path)
        cosmetic_paths_final.append(new_path2)

    for cosmetic in cosmetic_paths_final:
        cosmetic_file = Path(mod_folder) / cosmetic
        if not cosmetic_file.exists():
            cosmetic_file.parent.mkdir(exist_ok=True, parents=True)
        with open(cosmetic_file, 'w') as file:
            file.write("")

    new_vpk = vpk.new(str(mod_folder))
    new_vpk.save("Custom-Cosmetic-Disabler.vpk")
    models_folder = mod_folder / "models"
    if models_folder.exists():
        shutil.rmtree(models_folder)

    with open(disabled_cosmetics_file, 'w') as file:
        for filepath in cosmetic_paths:
            file.write(filepath + "\n")

    with open(disabled_cosmetics_names_file, "w") as file:
        for name in cosmetic_names:
            file.write(name + "\n")


def enable_cosmetic():
    print("Disabled Cosmetics:")
    print()
    for name in cosmetic_names:
        print(f"* {name}")
    print()
    print(f"{len(cosmetic_names)} cosmetics disabled.")
    print("Which cosmetic do you want to enable?")

    target_cosmetic_name = input("> ").strip().lower()
    cosmetics = find_cosmetics(tf2_dir + r"\tf\scripts\items\items_game.txt")

    for cosmetic in cosmetics: # Find target cosmetic
        cosmetic_name = cosmetic.get("name")

        if cosmetic_name == target_cosmetic_name:
            disabled_cosmetic_paths = cosmetic.get("paths")

            for path in disabled_cosmetic_paths:
                if path in cosmetic_paths:
                    cosmetic_paths.remove(path)
            cosmetic_names.remove(target_cosmetic_name)



def list_disabled_cosmetics():
    for name in cosmetic_names:
        print(name)
    print()
    print(f"{len(cosmetic_names)} cosmetics disabled.")

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

disabled_cosmetics_file = program_data / "data2" # Check for already disabled cosmetics and load path.
if disabled_cosmetics_file.exists():
    with open(str(disabled_cosmetics_file), "r") as file:
        for line in file:
            cosmetic_paths.append(line.replace("\n",""))
    print(cosmetic_paths)

disabled_cosmetics_names_file = program_data / "data3" # Check for already disabled cosmetics and load name
if disabled_cosmetics_names_file.exists():
    with open(str(disabled_cosmetics_names_file), "r") as file:
        for line in file:
            cosmetic_names.append(line.replace("\n",""))


print("Cosmetic Disabler Running.. What would you like to do?")
main_loop()