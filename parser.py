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

        for item_id, item in items.items():
            name = item.get("name")
            prefab = item.get("prefab", "").lower()
            slot = item.get("item_slot", "").lower()
            modelstyles = ""
            valid_classes = []

            #Get "used_by_classes" and store found classes
            used_by_classes = item.get("used_by_classes")
            if isinstance(used_by_classes, dict):
                for tf_class in used_by_classes:
                    if tf_class == "demoman":
                        valid_classes.append("demo")
                    else:
                        valid_classes.append(tf_class)

            # Detect cosmetics by prefab or slot
            cosmetic_keywords = [
                "hat", "misc", "paintable", "base_hat", "base_misc",
                "cosmetic", "tournament_medal", "tf_wearable"
            ]
            is_cosmetic = (
                    any(k in prefab for k in cosmetic_keywords)
                    or slot in ("head", "misc", "body", "feet")
            )

            # Grab nested basename if available
            basename = None
            mp = item.get("model_player_per_class")
            if isinstance(mp, dict):
                basename = mp.get("basename")

                if not valid_classes:
                    valid_classes = tf_classes

                if basename == "" or basename is None:
                    #basename = {}
                    basename = []
                    for TF_class, path in mp.items():
                        #basename[TF_class] = path
                        basename.append(path)
                elif basename != "" or basename is not None:
                    basename = [ basename.replace("%s", cls) for cls in valid_classes ]




            # Grab model_player if nested basename not found
            elif not isinstance(mp, dict):
                basename = item.get("model_player", None)
                if isinstance(basename, str):
                    #if "%s" in basename:
                       # basename = [
                            #basename.replace("%s", cls) for cls in valid_classes
                        #]
                    basename = [basename]

            visuals = item.get("visuals")

            if isinstance(visuals, dict):
                styles = visuals.get("styles")
                if isinstance(styles, dict):
                    #basename = []
                    if basename is None:
                        basename = []
                    for _, style_data in styles.items():
                        if not isinstance(style_data, dict):
                            continue

                        # Check both "model_player_per_class" and "model_player"
                        if "model_player_per_class" in style_data:
                            for _, path in style_data["model_player_per_class"].items():
                                if isinstance(path, str) and path.endswith(".mdl"):

                                    if not valid_classes:
                                        valid_classes = tf_classes

                                    path = [path.replace("%s", cls) for cls in valid_classes]
                                    #modelstyles.append(path)
                                    basename.extend(path)
                        elif "model_player" in style_data:
                            path = style_data["model_player"]
                            if isinstance(path, str) and path.endswith(".mdl"):
                                basename.append(path)


            #if is_cosmetic and item.get("hidden") != "1" and basename != "":
            if is_cosmetic and item.get("hidden") != "1":
                if prefab not in ("base_cosmetic_case", "base_keyless_cosmetic_case") and name not in ("Glitched Circuit Board", "Damaged Capacitor", "Web Easteregg Medal", "Tournament Medal (Armory)"):
                   #if basename == "" or basename is None:
                   basename = list(dict.fromkeys(basename))
                   cosmetics.append({
                       # "id": item_id,
                       "name": name.lower(),
                       "basename": basename,
                       # "modelstyles": modelstyles,
                       #"validclasses": valid_classes
                   })

    print(len(cosmetics))

    with open("tf2_cosmetics.csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        #writer.writerow(["name", "basename", "modelstyles", "validclasses"])
        writer.writerow(["name", "basename", "validclasses"])
        for c in cosmetics:
            #writer.writerow([c["name"] or "", c["basename"] or "", c["modelstyles"] or "", c["validclasses"] or ""])
            writer.writerow([c["name"] or "", c["basename"] or ""])

    print("COSMETICS RAN SUCCESSFULLY")
    return cosmetics