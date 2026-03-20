# this code will basically listen to events
# it needs to do one big embedding of all data
from encryption import EncryptionManager
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import json
import time
import os

# i might not need a seen_files (I dont think) maybe keep it in hashes instead thats what ill do 
# Get the folder this script lives in
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIRECTORIES_FILE = os.path.join(SCRIPT_DIR, "..", "data", "directories.txt")
DIRECTORIES_FILE = os.path.normpath(DIRECTORIES_FILE)  # a file where you can tell it which directories to scan for photos, one per line

DATA_FILE = "seenFiles.json.enc" # encrypted file on disk
PHOTO_EXTENSIONS = {".jpg", ".png", ".jpeg", ".gif"}
#DIRECTORIES_FILE = "../data/directories.txt" # a file where you can tell it which directories to scan for photos, one per line


# STEP 1: Check SeenFiles and check for new files in directories (this is on STARTUP)

encryptedManager = EncryptionManager(DATA_FILE)
seen_files = encryptedManager.file_contents # this is a dict now, we can use the keys as a set basically


# previous seen_files was a set()

new_files = []

# Read directories to scan )
with open(DIRECTORIES_FILE) as f: 
    directories = [line.strip() for line in f]

# Scan all directories
for directory in directories:
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in PHOTO_EXTENSIONS:
                path = os.path.join(root, file)
                if path not in seen_files:
                    print("New photo found on startup:", path)
                    new_files.append(path)
                    seen_files[path] = True  # add to seen files (using dict for O(1) lookups)

# Save updated seen files (make sure to encrypt it here)
#save_seen_files(seen_files, encryptedKey)
encryptedManager.file_contents = seen_files
encryptedManager.save_file_contents()

print("New photos since last run:", new_files)
print(f"seen_files: {len(seen_files)} total photos tracked.")
#print(f"{seen_files}")

# this needs to use the embedding code to compute the embeddings for the new files and add them to the saved embeddings
#    print("Computing embeddings... this may take a while.")
#    embeddings = encode_images(IMAGE_FOLDER, model)
#    save_embeddings(embeddings, EMBED_PATH)
#    print("Computed and saved embeddings.")

# STEP 2: Listen for new files and update seenFiles in real-time (this is after startup, it will keep running and listen for new files)


# fact check this code:
class PhotoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(tuple(PHOTO_EXTENSIONS)):
            print("New photo detected:", event.src_path)
            
            # THIS NEEDS ENCRYPTED SAVE INSTEAD probly....
            seen_files.add(event.src_path)
            with open(DATA_FILE, "w") as f:
                json.dump(list(seen_files), f)



# still need to implement embedding code

#observer = Observer()
#for directory in directories:
#    observer.schedule(PhotoHandler(), directory, recursive=True)

#observer.start()

#try:
#    while True:
#        time.sleep(1)
#except KeyboardInterrupt:
#    observer.stop()
#observer.join()