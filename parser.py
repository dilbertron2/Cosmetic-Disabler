from idlelib.run import uninstall_recursionlimit_wrappers
import vdf
import csv

tf_classes = [
    "scout", "soldier", "pyro", "demo", "heavy",
    "engineer", "medic", "sniper", "spy"
]

def find_cosmetics(file_path):
    cosmetics = []
    with open(file_path, encoding="utf-8") as file:
        data = vdf.load(file)
        items = data["items_game"]["items"]

        for item_id, item in items.items(): # Iterate through every single item in items_game.txt
            name = item.get("name")
            prefab = item.get("prefab", "").lower()
            slot = item.get("item_slot", "").lower()
            modelstyles = ""
            phy_bodygroup = False
            valid_classes = []


            used_by_classes = item.get("used_by_classes") # Get "used_by_classes" and store found classes
            if isinstance(used_by_classes, dict):
                for tf_class in used_by_classes:
                    if tf_class == "demoman":
                        valid_classes.append("demo")
                    else:
                        valid_classes.append(tf_class)


            cosmetic_keywords = [ # Detect cosmetics by prefab or slot
                "hat", "misc", "paintable", "base_hat", "base_misc",
                "cosmetic", "tournament_medal", "tf_wearable"
            ]
            is_cosmetic = (
                    any(k in prefab for k in cosmetic_keywords)
                    or slot in ("head", "misc", "body", "feet")
            )


            basename = None
            mp = item.get("model_player_per_class")
            if isinstance(mp, dict): # Grab nested basename if available
                basename = mp.get("basename")

                if not valid_classes:
                    valid_classes = tf_classes

                if basename == "" or basename is None:
                    #basename = {}
                    basename = []
                    for TF_class, path in mp.items():
                        #basename[TF_class] = path
                        basename.append(path)
                elif basename != "" or basename is not None: # Replace %s filepath placeholder with relevant classes
                    basename = [ basename.replace("%s", cls) for cls in valid_classes ]



            elif not isinstance(mp, dict): # Grab model_player if nested basename not found
                basename = item.get("model_player", None)
                if isinstance(basename, str):
                    #if "%s" in basename:
                       # basename = [
                            #basename.replace("%s", cls) for cls in valid_classes
                        #]
                    basename = [basename]

            visuals = item.get("visuals")

            if isinstance(visuals, dict):
                styles = visuals.get("styles") # Get cosmetic styles
                if isinstance(styles, dict):
                    #basename = []
                    if basename is None:
                        basename = []
                    for _, style_data in styles.items():
                        if not isinstance(style_data, dict):
                            continue


                        if "model_player_per_class" in style_data: # Check "model_player_per_class"
                            for _, path in style_data["model_player_per_class"].items():
                                if isinstance(path, str) and path.endswith(".mdl"):

                                    if not valid_classes:
                                        valid_classes = tf_classes

                                    path = [path.replace("%s", cls) for cls in valid_classes]
                                    #modelstyles.append(path)
                                    basename.extend(path)
                        elif "model_player" in style_data: # Check "model_player" if "model_player_per_class" not found
                            path = style_data["model_player"]
                            if isinstance(path, str) and path.endswith(".mdl"):
                                basename.append(path)

                target_bodygroups = visuals.get("player_bodygroups") # Get bodygroups
                if isinstance(target_bodygroups, dict):
                    for bodygroupname, value in target_bodygroups.items():
                        if bodygroupname in ("hat", "headphones"): # Check if bodygroups affect default headgear
                            phy_bodygroup = True
                            break


            if is_cosmetic and item.get("hidden") != "1":
                if prefab not in ("base_cosmetic_case", "base_keyless_cosmetic_case") and name not in ("Glitched Circuit Board", "Damaged Capacitor", "Web Easteregg Medal", "Tournament Medal (Armory)"):
                   #if basename == "" or basename is None:
                   basename = list(dict.fromkeys(basename)) # Remove duplicate filepaths
                   cosmetics.append({
                       #"id": item_id,
                       "name": name.lower(),
                       "paths": basename,
                       "phy_bodygroup": phy_bodygroup
                       #"modelstyles": modelstyles,
                       #"validclasses": valid_classes
                   })

    return cosmetics