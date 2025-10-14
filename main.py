import os
from parser import find_cosmetics
import vpk
import shutil
from pathlib import Path


tf2_default_dir = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2"
tf2_dir = r""
cosmetic_names = []
cosmetic_paths = []
mod_folder = Path().absolute() / "Cosmetic-Mod-Staging"
program_data = Path().absolute() / "Cosmetic Disabler Data"
replacement_folder = Path().absolute() / "Replacement Files"

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
        print(path)
        main, ext = os.path.splitext(path)
        new_path = main + ".vtx"
        cosmetic_paths_final.append(new_path)

        if any(sub in path for sub in ("sniper", "soldier", "engineer", "scout")):
            new_path = main + ".mdl"
            cosmetic_paths_final.append(new_path)
            new_path = main + ".phy"
            cosmetic_paths_final.append(new_path)
            new_path = main + ".vvd"
            cosmetic_paths_final.append(new_path)

    for cosmetic_file in cosmetic_paths_final:
        cosmetic_folder = (Path(mod_folder) / cosmetic_file).parent

        if not cosmetic_folder.exists():
            cosmetic_folder.mkdir(exist_ok=True, parents=True)

        main, ext = os.path.splitext(cosmetic_file)

        tf_class = next((sub for sub in ("sniper", "soldier", "engineer", "scout") if sub in cosmetic_file), None)

        if isinstance(tf_class, str): #Check if cosmetic belongs to either sniper, soldier, engineer or scout.
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

        elif not isinstance(tf_class, str) and ext == ".vtx": #If cosmetic doesn't belong to any of the above classes, execute this instead.
            with open(str(mod_folder.absolute()) + "/" + main + ".dx80.vtx", 'w') as file:
                file.write("")

            with open(str(mod_folder.absolute()) + "/" + main + ".dx90.vtx", 'w') as file:
                file.write("")

            with open(str(mod_folder.absolute()) + "/" + main + ".sw.vtx", 'w') as file:
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
    print("NOTICE: YOU MUST CREATE VPK FILE TO SAVE CHANGES TO DISABLED COSMETICS")
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