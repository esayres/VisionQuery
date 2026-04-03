import json
import os
import keyring
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

# this code basically handles encryption and decryption of the seenFiles.json file, which keeps track of which files have been processed. 
# It uses AES-GCM for encryption and stores the key securely using keyring. The file is encrypted on disk and decrypted in memory when needed.


# THIS NEEDS TO BE A CLASS, EMBEDDING ALSO NEEDS ENCRYPTION AS WELL


# --------------------------
# Configuration
# --------------------------
#SERVICE_NAME = "VisionQuery"
#KEY_NAME = "master_key"
#SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
#SEEN_FILE = os.path.join(SCRIPT_DIR, "..", "data", "seenFiles.json.enc")
#SEEN_FILE = os.path.normpath(SEEN_FILE)  # encrypted file on disk
#SEEN_FILE = "../data/seenFiles.json.enc"  # encrypted file on disk

class EncryptionManager:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file_extension = ".enc"
        self.service_name = "VisionQuery"
        self.key_name = "master_key"
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.encrypted_file = os.path.join(SCRIPT_DIR, "..", "data", f"{self.file_name}") # missing the extension here
        self.encrypted_file = os.path.normpath(self.encrypted_file)  # encrypted file on disk
        self.chunk_size = 5000 # number of embedding to store per file to avoid overflow errors
        #self.file_contents = {} # start with empty set if loading fails
        
        self.aesgcm = self.get_encryption_key()
        try:
            self.file_contents = self.load_file_contents() #
            #print(self.file_contents)
            print(f"encrypted {self.file_name}{self.file_extension} loaded successfully.")
        except Exception as e:
            print(f"Error loading {self.file_name}{self.file_extension} files, starting with empty dictionary. Error:", e)
            self.file_contents = {} # start with empty set if loading fails

    # --------------------------
    # 1. Get or generate encryption key
    # --------------------------
    def get_encryption_key(self):
        key_b64 = keyring.get_password(self.service_name , self.key_name)

        if key_b64 is None:
            # Generate 32-byte AES key
            key = AESGCM.generate_key(bit_length=256)
            key_b64 = base64.b64encode(key).decode()
            keyring.set_password(self.service_name, self.key_name, key_b64)
        else:
            key = base64.b64decode(key_b64)

        aesgcm = AESGCM(key)
        return aesgcm

    # --------------------------
    # 2. Helper functions
    # --------------------------
    def encrypt_json(self, data):
        """Encrypts Python object as JSON and returns bytes."""
        json_bytes = json.dumps(data).encode()
        nonce = os.urandom(12)  # AESGCM nonce
        ciphertext = self.aesgcm.encrypt(nonce, json_bytes, None)
        return base64.b64encode(nonce + ciphertext).decode()


    def decrypt_json(self, encrypted_str):
        """Decrypts bytes from encrypted string to Python object."""
        raw = base64.b64decode(encrypted_str)
        if len(raw) < 12:
            raise ValueError("Encrypted data too short to contain a nonce")
        nonce = raw[:12]
        ciphertext = raw[12:]
        json_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(json_bytes)

    # --------------------------
    # 3. Load or initialize seen files
    # --------------------------
    def load_file_contents(self):  # this runs somehow when the model is init?
        file_contents = []
        print(f"{self.encrypted_file}_chunk_0{self.file_extension}")
        for i in range(0, 100000): # just a random large number to prevent infinite loop, it will break when it cant find the next chunk file
            chunk_file = f"{self.encrypted_file}_chunk_{i}{self.file_extension}"
            if os.path.exists(chunk_file):
                with open(chunk_file, "r") as f:
                    chunk_contents = self.decrypt_json(f.read())
                    file_contents.extend(chunk_contents)
            else:
                if i == 0: # no chunks
                    print("no Chucks FIle Found")
                    break  # no more chunk files, exit loop
                print(f"ended at chunk {i - 1} file")
                break
        self.file_contents = file_contents
        return file_contents


      # if os.path.exists(self.encrypted_file):
     #       with open(self.encrypted_file, "r") as f:
      #          file_contents = self.decrypt_json(f.read())
     #   else:
     #       file_contents = {}  # use hash as key (we dont need to hash)
     #   return file_contents

    # --------------------------
    # 5. Save encrypted seenFiles.json
    # --------------------------
    def save_file_contents(self):
        #try:
        #    items = list(self.file_contents.items())
        #except AttributeError:
        #    items = list(self.file_contents)
        for chunk_index, i in enumerate(range(0, len(self.file_contents), self.chunk_size)):
            chunk = self.file_contents[i:i + self.chunk_size]
            print(f"Saving chunk {i // self.chunk_size} of {self.file_name}{self.file_extension}...")
            


            with open(f"{self.encrypted_file}_chunk_{chunk_index}{self.file_extension}", "w") as f: # this needs to save to multiple files
                f.write(self.encrypt_json(chunk))

            print(f"Encrypted {self.file_name}_chunk_{chunk_index}{self.file_extension} saved.")

    # --------------------------
    # 4. Example: add a file
    # --------------------------
    #file_path = "/home/photo.png"
    #seen_files[file_path] = {"last_seen": 1712345678} # any extra medata can go here
