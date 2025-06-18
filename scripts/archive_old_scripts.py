import os
import shutil

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # path to PokeApp
scripts_path = os.path.join(root, 'scripts')
archive_path = os.path.join(root, 'Archive')

# Create the Archive folder if it doesn't exist
os.makedirs(archive_path, exist_ok=True)

# List of script files to move
files_to_archive = [
    'populate_dynamodb.py',
    'populate_pokedex.py',
    'populate_sets.py',
    'query_cards.py'
]

for filename in files_to_archive:
    src = os.path.join(scripts_path, filename)
    dest = os.path.join(archive_path, filename)
    if os.path.exists(src):
        shutil.move(src, dest)
        print(f"✅ Moved {filename} to Archive/")
    else:
        print(f"⚠️ File not found: {filename}")

print("\n🎉 Archive complete.")
