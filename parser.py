from idlelib.run import uninstall_recursionlimit_wrappers

items_game_path_test = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2\tf\scripts\items\items_game.txt"

import vdf
import csv


def find_cosmetics(file_path=items_game_path_test):
    cosmetics = []
    with open(file_path, encoding="utf-8") as file:
        data = vdf.load(file)
        items = data["items_game"]["items"]

        for item_id, item in items.items():
            name = item.get("name")
            prefab = item.get("prefab", "").lower()
            slot = item.get("item_slot", "").lower()
            modelstyles = ""

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

                if basename == "" or basename is None:
                    basename = {}
                    for TF_class, path in mp.items():
                        basename[TF_class] = path
            # Grab model_player if nested basename not found
            elif not isinstance(mp, dict):
                basename = item.get("model_player", None)
                #mp = item.get("model_player")
                #if isinstance(mp, dict):

            visuals = item.get("visuals")

            if isinstance(visuals, dict):
                styles = visuals.get("styles")
                if isinstance(styles, dict):
                    modelstyles = []
                    for _, style_data in styles.items():
                        if not isinstance(style_data, dict):
                            continue

                        # Check both "model_player_per_class" and "model_player"
                        if "model_player_per_class" in style_data:
                            for _, path in style_data["model_player_per_class"].items():
                                if isinstance(path, str) and path.endswith(".mdl"):
                                    modelstyles.append(path)
                        elif "model_player" in style_data:
                            path = style_data["model_player"]
                            if isinstance(path, str) and path.endswith(".mdl"):
                                modelstyles.append(path)


            #if is_cosmetic and item.get("hidden") != "1" and basename != "":
            if is_cosmetic and item.get("hidden") != "1":
                if prefab not in ("base_cosmetic_case", "base_keyless_cosmetic_case") and name not in ("Glitched Circuit Board", "Damaged Capacitor", "Web Easteregg Medal", "Tournament Medal (Armory)"):
                   #if basename == "" or basename is None:
                        cosmetics.append({
 #                           "id": item_id,
                            "name": name,
                            "basename": basename,
                            "modelstyles": modelstyles,
                        })

    print(len(cosmetics))

    with open("tf2_cosmetics.csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "name", "basename", "modelstyles"])
        for c in cosmetics:
            writer.writerow([c["name"] or "", c["basename"] or "", c["modelstyles"] or ""])




find_cosmetics()

