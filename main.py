import os
import vpk
import shutil
from pathlib import Path


tf2_default_dir = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2"
tf2_dir = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2"
paths_txt = "paths.txt"
cosmetic_paths = []
mod_folder = Path().absolute() / "Cosmetic-Mod-Staging"

if not mod_folder.exists():
    mod_folder.mkdir()


def get_custom_dir():
    print(r"Enter the full path of your TF2 installation. (..steamapps\common\Team Fortress 2)")
    user_input_dir = input()
    if os.path.exists(user_input_dir):
        tf2_dir = user_input_dir
    else:
        print("Invalid!")
        get_custom_dir()

def get_user_hat():
    print("What cosmetic would you like to remove? Paste cosmetic file name.")
    user_hat_name = input().lower()
    with open(paths_txt) as file:
        for line in file:
            if user_hat_name in line:
                cosmetic_paths.append(line.replace("\n",""))

def create_vpk():
    for cosmetic in cosmetic_paths:
        cosmetic_file = Path(mod_folder) / cosmetic
        if not cosmetic_file.exists():
            cosmetic_file.parent.mkdir(exist_ok=True, parents=True)
        with open(cosmetic_file, 'w') as file:
            file.write("")

    new_vpk = vpk.new(str(mod_folder))
    new_vpk.save("mod_test.vpk")
    models_folder = mod_folder / "models"
    shutil.rmtree(models_folder)



if os.path.exists(tf2_default_dir):
    print("TF2 install location detected as: " + tf2_default_dir)
    print("Is this correct? Y/N")
    user_input = input().upper()
    if user_input == "N" or user_input == "NO":
        get_custom_dir()

elif not os.path.exists(tf2_default_dir):
    get_custom_dir()

get_user_hat()
print(cosmetic_paths)
create_vpk()