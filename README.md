Rename + Refactor Script

This Python tool cleans up our player video folders.
It renames all the .mp4 and .json files to a consistent format, fixes up the JSON contents, and updates the player’s URL mapping CSV.

What it does

Walks through all folders under a player’s directory (including /bad folders)

Renames files like
Keldon_Johnson_3points_1.mp4 → Keldon Johnson_3pt_001.mp4

Fixes every video_name, class_name, and player_name inside the JSONs

Updates the player’s *_url_mapping.csv with the new clip names

Prints any files it’s unsure about instead of breaking them

How to use it

Clone the repo

git clone https://github.com/<your-org>/<repo-name>.git
cd <repo-name>


Run the script

python rename_refactor_videos.py


When prompted, enter:

Player's first name:  Keldon
Player's last name:   Johnson
Path to folder:       C:\path\to\Keldon_Johnson


That’s it — the script will update everything in that folder and its subfolders.
Keep a backup just in case (the script overwrites the originals).

Notes

Works for both .mp4 and .json files.

Only changes names that match the standard format — anything weird gets skipped and reported.

The CSV (Firstname_Lastname_url_mapping.csv) gets renamed too (to Firstname Lastname_url_mapping.csv).

Example:
Before → Keldon_Johnson_3points_23.mp4
After → Keldon Johnson_3pt_023.mp4
