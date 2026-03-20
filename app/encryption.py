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
        self.service_name = "VisionQuery"
        self.key_name = "master_key"
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.encrypted_file = os.path.join(SCRIPT_DIR, "..", "data", file_name)
        self.encrypted_file = os.path.normpath(self.encrypted_file)  # encrypted file on disk
        
        self.aesgcm = self.get_encryption_key()
        try:
            self.file_contents = self.load_file_contents() #
            print(f"encrypted {self.file_name} loaded successfully.")
        except Exception as e:
            print(f"Error loading {self.file_name} files, starting with empty dictionary. Error:", e)
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
    def load_file_contents(self):
        if os.path.exists(self.encrypted_file):
            with open(self.encrypted_file, "r") as f:
                file_contents = self.decrypt_json(f.read())
        else:
            file_contents = {}  # use hash as key (we dont need to hash)
        return file_contents

    # --------------------------
    # 5. Save encrypted seenFiles.json
    # --------------------------
    def save_file_contents(self):
        with open(self.encrypted_file, "w") as f:
            f.write(self.encrypt_json(self.file_contents))

        print(f"Encrypted {self.file_name} saved.")

    # --------------------------
    # 4. Example: add a file
    # --------------------------
    #file_path = "/home/photo.png"
    #seen_files[file_path] = {"last_seen": 1712345678} # any extra medata can go here
