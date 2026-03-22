import sys
import os

# Add the parent directory (PROJECT_FILE) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#from model.model import SomeFunction

#try: # probly a better way but this allows me to run the code from listener and run
from app.encryption import EncryptionManager

from models.clipModel import CLIPWrapper


from PIL import Image
#import os
import torch
import pickle

encryptionManager = EncryptionManager("embeddings")

# so we should Chunk our embedding files into multiple files (roughly 5-10k photos each)
# i made the mistake of trying to save all the embedding in one file and that completely broke (OverflowError: data or associated data too long. max 2**31 - 1)


def encode_images(folder_path, model): # this func isnt used anymore (orginal ver before real-time listener)
    embeddings = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(root, file)

                try:
                    image = Image.open(path).convert("RGB")
                    emb = model.encode_image(image)
                    embeddings.append((path, emb)) # so this needs to be encrypted when we save it,
                except Exception as e:
                    print(f"Skipping {path}: {e}")

    return embeddings

def encode_images_paths(loadedEmbeddings, paths):
    """
    Add embeddings for new image paths to loadedEmbeddings, 
    deduplicating automatically and saving to disk.
    """
    # Convert loaded embeddings to a dict for fast deduplication
    embeddings_dict = {path: emb for path, emb in loadedEmbeddings}

    model = CLIPWrapper()
    for photo in paths:
        if photo in embeddings_dict:
            print(f"Skipping {photo}: already embedded")
            continue  # skip duplicates

        try:
            image = Image.open(photo).convert("RGB")
            emb = model.encode_image(image)
            embeddings_dict[photo] = emb  # add new embedding
            print(f"Encoded {photo} added to embeddings.")
        except Exception as e:
            print(f"Skipping {photo}: {e}")

    # Convert dict back to list and save
    deduped_embeddings = list(embeddings_dict.items()) # this might not be needed anymore Ill look into later
    save_embeddings(deduped_embeddings)

    del model
    #return deduped_embeddings  # optional, useful if you want the updated list immediately


def save_embeddings(embeddings): #so this needs to gather all embedding.enc files and load then all in. 
    serializable_embeddings = [(path, emb.squeeze().tolist()) for path, emb in embeddings] # # converts tensor to list so it can be JSON serialized
    encryptionManager.file_contents = serializable_embeddings
    encryptionManager.save_file_contents()


def load_embeddings():
    data = encryptionManager.file_contents
    return [(path, torch.tensor(emb)) for path, emb in data]
