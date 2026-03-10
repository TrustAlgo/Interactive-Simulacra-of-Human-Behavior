"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: compress_sim_storage.py
Description: Compresses a simulation for replay demos.
"""

import json
import shutil
from pathlib import Path
from global_methods import find_filenames, create_folder_if_not_there


def compress(sim_code: str):

    base = Path("../environment/frontend_server")
    sim_storage = base / "storage" / sim_code
    compressed_storage = base / "compressed_storage" / sim_code

    persona_folder = sim_storage / "personas"
    move_folder = sim_storage / "movement"
    meta_file = sim_storage / "reverie" / "meta.json"

    # --------------------------------
    # Get persona names
    # --------------------------------
    persona_names = [
        Path(p).name
        for p in find_filenames(str(persona_folder), "")
        if not Path(p).name.startswith(".")
    ]

    # --------------------------------
    # Get max movement file index
    # --------------------------------
    move_files = find_filenames(str(move_folder), "json")

    max_move_count = max(
        int(Path(f).stem)
        for f in move_files
    )

    persona_last_move = {}
    master_move = {}

    # --------------------------------
    # Process movement files
    # --------------------------------
    for step in range(max_move_count + 1):

        master_move[step] = {}

        with open(move_folder / f"{step}.json") as f:
            move_dict = json.load(f)["persona"]

        for p in persona_names:

            current = move_dict[p]

            if step == 0:
                changed = True
            else:
                last = persona_last_move[p]

                changed = (
                    current["movement"] != last["movement"]
                    or current["pronunciatio"] != last["pronunciatio"]
                    or current["description"] != last["description"]
                    or current["chat"] != last["chat"]
                )

            if changed:
                data = {
                    "movement": current["movement"],
                    "pronunciatio": current["pronunciatio"],
                    "description": current["description"],
                    "chat": current["chat"],
                }

                persona_last_move[p] = data
                master_move[step][p] = data

    # --------------------------------
    # Write compressed result
    # --------------------------------
    create_folder_if_not_there(str(compressed_storage))

    with open(compressed_storage / "master_movement.json", "w") as f:
        json.dump(master_move, f, indent=2)

    shutil.copyfile(meta_file, compressed_storage / "meta.json")

    shutil.copytree(
        persona_folder,
        compressed_storage / "personas",
        dirs_exist_ok=True
    )


if __name__ == "__main__":
    compress("July1_the_ville_isabella_maria_klaus-step-3-9")
