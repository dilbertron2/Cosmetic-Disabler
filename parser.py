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


# // LICENSE FOR VDF LIBRARY //

# Copyright (c) 2015 Rossen Georgiev <rossen@rgp.io>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
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


from pathlib import Path

import re
import vdf
from valve_parsers import VPKFile

tf_classes = [
    "scout", "soldier", "pyro", "demo", "heavy",
    "engineer", "medic", "sniper", "spy"
]

cosmetic_keywords = [  # Detect cosmetics by prefab or slot
    "hat", "misc", "paintable", "base_hat", "base_misc",
    "cosmetic", "tournament_medal", "tf_wearable", "grenades",
    "backpack", "beard", "zombie"
]

localisation_dict = None


def check_files_in_VPK(vpk: VPKFile, path: str):  # Check if given path exists in given VPK file
    if vpk and path:
        target_path = vpk.find_files(path)
        if target_path:
            return True

    return False


def get_loc_string(target_str: str):
    global localisation_dict

    if localisation_dict:
        loc_string = localisation_dict.get(target_str)
        return loc_string
    return None


def find_cosmetics(file_path: Path, misc_dir_location):
    global localisation_dict

    if not localisation_dict:  # On first search find the english loc file and load every loc string into a dictionary
        loc_file = (file_path.parent.parent.parent / "resource" / "tf_english.txt")
        if loc_file.exists():
            localisation_dict = {}
            pattern = re.compile(r'^\s*"([^"]+)"\s*"([^"]+)"')

            with open(loc_file, 'r', encoding="utf-16-le") as file:
                for line in file:
                    match = pattern.match(line)

                    if match:
                        key, value = match.groups()
                        localisation_dict[key] = value
    prefabs = {}
    cosmetics = []

    with open(file_path, encoding="utf-8") as file:
        data = vdf.load(file)
        item_prefabs = data["items_game"]["prefabs"]
        items = data["items_game"]["items"]

        for prefab_name, prefab in item_prefabs.items(): # Get all prefabs in items_game.txt
            slot = prefab.get("item_slot", "").lower()
            inheriting_prefab = prefab.get("prefab", "")
            is_cosmetic = slot in ("head", "misc", "body", "feet") or any(k in inheriting_prefab for k in ("hat", "misc"))

            if is_cosmetic:
                prefabs[prefab_name] = prefab

        for item_id, item in items.items():  # Iterate through every single item in items_game.txt
            name = item.get("name", "")
            prefab = item.get("prefab", "").lower()
            slot = item.get("item_slot", "").lower()
            item_loc_name = item.get("item_name", "").replace("#", "")
            modelstyles = ""
            bodygroups = []
            phy_bodygroup = False
            valid_classes = []

            # Item inherits all/most stats from prefab
            if prefab in ("pyrovision_goggles", "triad_trinket", "champ_stamp", "marxman", "cannonball", "item_bak_fear_monger","item_bak_arkham_cowl", "item_bak_firefly"):
                item = prefabs[prefab]
                # Rerun item checks now that prefab replaces item info
                if not name:
                    name = item.get("name")
                if not prefab:
                    prefab = item.get("prefab", "").lower()
                if not slot:
                    slot = item.get("item_slot", "").lower()
                    if not slot:
                        slot = "misc"
                if not item_loc_name:
                    item_loc_name = item.get("item_name", "").replace("#", "")


            is_cosmetic = (
                    any(k in prefab for k in cosmetic_keywords)
                    or slot in ("head", "misc", "body", "feet")
            )

            if is_cosmetic: # Check if current item is cosmetic before running any other checks, saving lots of time
                if prefab:  # Get default bodygroups from prefab
                    if prefab == "backpack" or prefab.startswith("backpack ") or " backpack" in prefab:
                        bodygroups.append("backpack")
                    if prefab == "promo hat" or prefab.startswith("promo hat ") or " promo hat" in prefab:
                        bodygroups.extend(["hat", "headphones"])
                    if prefab == "hat" or prefab.startswith("hat ") or " hat" in prefab:
                        bodygroups.append("hat")

                used_by_classes = item.get("used_by_classes")  # Get "used_by_classes" and store found classes
                if isinstance(used_by_classes, dict):
                    for tf_class in used_by_classes:
                        if tf_class.lower() == "demoman":
                            valid_classes.append("demo")
                        else:
                            valid_classes.append(tf_class)

                basename = None
                mp = item.get("model_player_per_class")
                if isinstance(mp, dict):  # Grab nested basename if available
                    basename = mp.get("basename")

                    if not valid_classes:
                        valid_classes = tf_classes

                    if basename == "" or basename is None:
                        basename = []
                        for TF_class, path in mp.items():
                            basename.append(path)
                    elif basename != "" or basename is not None:  # Replace %s filepath placeholder with relevant classes
                        basename = [basename.replace("%s", cls) for cls in valid_classes]


                elif not isinstance(mp, dict):  # Grab model_player if nested basename not found
                    basename = item.get("model_player", None)
                    if isinstance(basename, str):
                        basename = [basename]

                visuals = item.get("visuals")

                if isinstance(visuals, dict):
                    styles = visuals.get("styles")  # Get cosmetic styles
                    if isinstance(styles, dict):
                        # basename = []
                        if basename is None:
                            basename = []
                        for _, style_data in styles.items():
                            if not isinstance(style_data, dict):
                                continue

                            if "model_player_per_class" in style_data:  # Check "model_player_per_class"
                                for _, path in style_data["model_player_per_class"].items():
                                    if isinstance(path, str) and path.endswith(".mdl"):

                                        if not valid_classes:
                                            valid_classes = tf_classes

                                        path = [path.replace("%s", cls) for cls in valid_classes]
                                        # modelstyles.append(path)
                                        basename.extend(path)
                            elif "model_player" in style_data:  # Check "model_player" if "model_player_per_class" not found
                                path = style_data["model_player"]
                                if isinstance(path, str) and path.endswith(".mdl"):
                                    basename.append(path)

                            elif "additional_hidden_bodygroups" in style_data:  # Check for bodygroups of styles if they exist
                                for bodygroup, value in style_data["additional_hidden_bodygroups"].items():
                                    if bodygroup and value == "1":
                                        bodygroups.append(bodygroup)

                    target_bodygroups = visuals.get("player_bodygroups")  # Get bodygroups
                    if isinstance(target_bodygroups, dict):
                        for bodygroupname, value in target_bodygroups.items():
                            if value == "1":
                                bodygroups.append(bodygroupname)

                if item.get("hidden") != "1":
                    if prefab not in ("base_cosmetic_case", "base_keyless_cosmetic_case") and name not in (
                            "Glitched Circuit Board", "Damaged Capacitor", "Web Easteregg Medal",
                            "Tournament Medal (Armory)", "Voodoo-Cursed Soul (Armory)") and "GateBot" not in name:

                        # Just before we add to cosmetic list, check if loc string exists, if it does, replace name with name from loc file
                        if item_loc_name:
                            loc_string = get_loc_string(item_loc_name)
                            if loc_string:
                                name = loc_string

                        # Check all bodygroups to see if cosmetic can fall off of player upon death
                        phy_bodygroup = any(bg in ("hat", "headphones", "dogtags") for bg in bodygroups)

                        if basename:
                            if not isinstance(basename, list):
                                basename = [basename]

                            paths_to_add = []
                            for path in basename:
                                path = Path(path)
                                main, ext = path.with_suffix(''), path.suffix
                                paths_to_add.append(f"{main}.vtx")
                                paths_to_add.append(f"{main}.vvd")
                                if phy_bodygroup:
                                    paths_to_add.append(f"{main}.phy")

                            basename.extend(paths_to_add)

                        basename = list(dict.fromkeys(basename))  # Remove duplicate filepaths


                        cosmetics.append({
                            # "id": item_id,
                            # "name": name.lower(),
                            "name": name,
                            "paths": basename,
                            "phy_bodygroup": phy_bodygroup,
                            "bodygroups": bodygroups
                            # "modelstyles": modelstyles,
                            # "validclasses": valid_classes
                        })


    unique_cosmetics = [] # Remove duplicate cosmetics
    seen_names = set()

    for cosmetic in cosmetics:
        name = cosmetic.get("name", "").lower()
        if name not in seen_names:
            seen_names.add(name)
            unique_cosmetics.append(cosmetic)

    cosmetics = unique_cosmetics

    return cosmetics