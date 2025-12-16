
import os
import json
import struct
import sys
from collections import Counter

def deserializeAction(action_byte):
    actions = {
        "jump": bool((action_byte >> 4) & 1),
        "rush": bool((action_byte >> 3) & 1),
        "duck": bool((action_byte >> 2) & 1)
    }
    return actions

def get_mario_state_name(state_id):
    if state_id == 0:
        return "mario"
    elif state_id == 1:
        return "largemario"
    elif state_id == 2:
        return "fireMario"
    return "unknown"


def process_files(reps_dir, jsons_dir):
    for rep_filename in os.listdir(reps_dir):
        if not rep_filename.endswith(".rep"):
            continue

        basename = os.path.splitext(rep_filename)[0]
        json_filename = basename + ".json"
        rep_filepath = os.path.join(reps_dir, rep_filename)
        json_filepath = os.path.join(jsons_dir, json_filename)

        if not os.path.exists(json_filepath):
            print(f"Skipping {rep_filename}: Corresponding json file not found.")
            continue

        with open(rep_filepath, 'rb') as f:
            rep_data = f.read()

        with open(json_filepath, 'r') as f:
            try:
                json_data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping {json_filename}: Invalid JSON.")
                continue

        element_data = json_data.get("elementData1", [])
        if not element_data or len(element_data) < 2:
            print(f"Skipping {json_filename}: No elementData1 found or not enough data.")
            continue
        
        print(f"Processing {rep_filename} with {len(rep_data)} frames and {len(element_data)-1} json frames.")
        # Skip the first element which is not a frame
        element_data = element_data[1:]

        processed_data = []
        num_frames = min(len(rep_data), len(element_data))

        for i in range(num_frames):
            frame_data = element_data[i]
            if not (frame_data and "marioX1" in frame_data and "marioY2" in frame_data):
                continue

            x_coord = frame_data["marioX1"]
            y_coord = frame_data["marioY2"]
            mario_state = frame_data.get("marioState3", 0)
            mario_state_name = get_mario_state_name(mario_state)

            action_byte = rep_data[i]
            actions = deserializeAction(action_byte)

            data_to_append = {
                "pos": [x_coord, y_coord, i],
                "jump": actions["jump"],
                "duck": actions["duck"],
                "marioState": mario_state_name
            }

            if mario_state_name == "fireMario":
                data_to_append["shot"] = actions["rush"]
            else:
                data_to_append["rush"] = actions["rush"]
            
            processed_data.append(data_to_append)

        output_filename = basename + ".json"
        with open(output_filename, 'w') as f:
            json.dump(processed_data, f, indent=4)
        
        print(f"Processed {rep_filename} and saved to {output_filename}")

if __name__ == "__main__":
    reps_directory = "reps"
    jsons_directory = "jsons"
    process_files(reps_directory, jsons_directory)
