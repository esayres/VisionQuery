from PIL import Image
import os
import sys
import torch


# Add the parent directory (PROJECT_FILE) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.encryption import EncryptionManager
from app.faissManager import load_or_create_index, save_index, add_embeddings_to_index
from models.clipModel import CLIPWrapper

# Two separate stores: one for the FAISS index (unencrypted, binary),
# one for the ordered path list (encrypted)
pathManager = EncryptionManager("embeddings_paths")

def encode_images_paths(paths):
    """
    Encode new images, add to FAISS index, update encrypted path list.
    """
    index = load_or_create_index()

    # Load existing ordered path list
    existing_paths = pathManager.file_contents
    if not isinstance(existing_paths, list):
        existing_paths = []

    existing_set = set(existing_paths)

    new_pairs = []
    model = CLIPWrapper()

    for photo in paths:
        if photo in existing_set:
            print(f"Skipping {photo}: already embedded")
            continue
        try:
            image = Image.open(photo).convert("RGB")
            emb = model.encode_image(image)
            new_pairs.append((photo, emb))
            print(f"Encoded {photo}")
        except Exception as e:
            print(f"Skipping {photo}: {e}")

    del model

    if new_pairs:
        add_embeddings_to_index(index, new_pairs)
        save_index(index)

        # Append new paths in the same order they were added to FAISS
        for path, _ in new_pairs:
            existing_paths.append(path)

        pathManager.file_contents = existing_paths
        pathManager.save_file_contents()

    print(f"FAISS index now has {index.ntotal} vectors.")

def load_paths():
    """Return the ordered path list (mirrors FAISS index positions)."""
    paths = pathManager.file_contents
    return paths if isinstance(paths, list) else []

def load_embeddings():
    data = pathManager.file_contents
    return [(path, torch.tensor(emb)) for path, emb in data]