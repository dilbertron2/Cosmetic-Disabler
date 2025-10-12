import os
import vpk

models_vpk =  vpk.open(r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2\tf\tf2_misc_dir.vpk")
#models_folder = models_vpk.get_file("models/player")
paths_file = open("paths.txt", "a")
for file in models_vpk:
    if "models/player/items" in file and not "materials" in file and ".vtx" in file and not "taunts" in file and not "taunt" in file and not "crafting" in file:
        paths_file.write(file + "\n")
    if "models/workshop/player/items" in file and ".vtx" in file and not "taunts" in file and not "taunt" in file:
        paths_file.write(file + "\n")
    if "models/workshop_partner/player/items" in file and ".vtx" in file and not "taunts" in file and not "taunt" in file:
        paths_file.write(file + "\n")