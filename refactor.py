import os
import re
import json
import csv
from pathlib import Path


def normalize_shot_type(shot_type: str) -> str:
    """Normalize shot type to '3pt' or 'freethrow'."""
    shot_type_lower = shot_type.lower()
    if shot_type_lower in ["3points", "3pts", "3pt"]:
        return "3pt"
    elif shot_type_lower == "freethrow":
        return "freethrow"
    return shot_type  # unknown type, return as-is for logging


def pad_video_number(num_str: str) -> str:
    """Convert video number to 3-digit zero-padded string."""
    try:
        num = int(num_str)
        return f"{num:03d}"
    except ValueError:
        return num_str  # leave unchanged if not numeric


def rename_file(file_path: Path, player_first: str, player_last: str, uncertain_files: list):
    """Rename a single .mp4 or .json file and refactor .json content if needed."""
    filename = file_path.name
    extension = file_path.suffix.lower()

    # Regex to match patterns like: Player_First_Last_3points_23.mp4
    pattern = rf"({player_first})[_ ]({player_last})[_ ](3points|3pts|3pt|freethrow)[_ ](\d+){extension}"
    match = re.match(pattern, filename, re.IGNORECASE)

    if not match:
        uncertain_files.append(str(file_path))
        return

    first, last, shot_type, num = match.groups()

    # Normalize parts
    new_shot_type = normalize_shot_type(shot_type)
    new_num = pad_video_number(num)
    new_name = f"{player_first} {player_last}_{new_shot_type}_{new_num}{extension}"

    new_path = file_path.with_name(new_name)

    # Rename file
    if new_path != file_path:
        file_path.rename(new_path)

    # Refactor JSON content if applicable
    if extension == ".json":
        try:
            with open(new_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            def refactor_json_entry(entry):
                """Recursively update video_name, class_name, and player_name."""
                if isinstance(entry, dict):
                    for key, value in entry.items():
                        if key == "video_name" and isinstance(value, str):
                            entry[key] = new_name.replace(".json", ".mp4")
                        elif key == "class_name" and isinstance(value, str):
                            entry[key] = normalize_shot_type(value)
                        elif key == "player_name" and isinstance(value, str):
                            entry[key] = value.replace("_", " ")
                        else:
                            refactor_json_entry(value)
                elif isinstance(entry, list):
                    for item in entry:
                        refactor_json_entry(item)

            refactor_json_entry(data)

            with open(new_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            print(f"⚠️ Failed to refactor JSON: {new_path} — {e}")
            uncertain_files.append(str(new_path))


def update_url_mapping_csv(player_dir: Path, player_first: str, player_last: str, uncertain_files: list):
    """Update the player's URL mapping CSV according to renaming rules."""
    old_csv_name = f"{player_first}_{player_last}_url_mapping.csv"
    old_csv_path = player_dir / old_csv_name

    if not old_csv_path.exists():
        print(f"⚠️ No URL mapping CSV found for {player_first} {player_last}. Skipping CSV update.")
        return

    new_csv_name = f"{player_first} {player_last}_url_mapping.csv"
    new_csv_path = player_dir / new_csv_name

    updated_rows = []
    try:
        with open(old_csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if not fieldnames or "Clip Name" not in fieldnames:
                print(f"⚠️ CSV format unexpected: {old_csv_path}")
                return
            for row in reader:
                clip_name = row["Clip Name"]
                ext = Path(clip_name).suffix
                pattern = rf"({player_first})[_ ]({player_last})[_ ](3points|3pts|3pt|freethrow)[_ ](\d+){ext}"
                match = re.match(pattern, clip_name, re.IGNORECASE)

                if match:
                    _, _, shot_type, num = match.groups()
                    new_shot_type = normalize_shot_type(shot_type)
                    new_num = pad_video_number(num)
                    new_clip_name = f"{player_first} {player_last}_{new_shot_type}_{new_num}{ext}"
                    row["Clip Name"] = new_clip_name
                else:
                    uncertain_files.append(f"CSV: {clip_name}")
                updated_rows.append(row)

        with open(new_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

        # Remove old CSV after successful rewrite
        old_csv_path.unlink(missing_ok=True)
        print(f"✅ Updated and renamed CSV: {new_csv_path}")

    except Exception as e:
        print(f"⚠️ Failed to process CSV {old_csv_path}: {e}")
        uncertain_files.append(str(old_csv_path))


def process_player_directory(player_dir: str, player_first: str, player_last: str):
    """Walk through the directory and rename/refactor files + update URL CSV."""
    player_dir = Path(player_dir)
    uncertain_files = []

    if not player_dir.exists():
        print(f"❌ Directory not found: {player_dir}")
        return

    # --- Step 1: Update URL mapping CSV ---
    update_url_mapping_csv(player_dir, player_first, player_last, uncertain_files)

    # --- Step 2: Process all .mp4 and .json files recursively ---
    for root, _, files in os.walk(player_dir):
        for file in files:
            if file.lower().endswith((".mp4", ".json")):
                file_path = Path(root) / file
                rename_file(file_path, player_first, player_last, uncertain_files)

    print("\n✅ Renaming and refactoring complete.")
    if uncertain_files:
        print("\n⚠️ The following files were skipped or uncertain:")
        for f in uncertain_files:
            print("   ", f)
    else:
        print("\n🎉 All files processed successfully.")



if __name__ == "__main__":
    # Example input:
    # player_first = "Keldon"
    # player_last = "Johnson"
    # player_dir = "C:/path/to/Keldon_Johnson"

    player_first = input("Enter player's first name: ").strip()
    player_last = input("Enter player's last name: ").strip()
    player_dir = input("Enter path to player's directory: ").strip()

    process_player_directory(player_dir, player_first, player_last)
