from app.encryption import EncryptionManager
from PIL import Image
import os
import torch
import pickle

encryptionManager = EncryptionManager("embeddings.enc")

def encode_images(folder_path, model):
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


def save_embeddings(embeddings, path="data/embeddings.pkl"):
    serializable_embeddings = [(path, emb.squeeze().tolist()) for path, emb in embeddings] # # converts tensor to list so it can be JSON serialized
    encryptionManager.file_contents = serializable_embeddings
    encryptionManager.save_file_contents()


def load_embeddings(path="data/embeddings.pkl"):
    data = encryptionManager.file_contents
    return [(path, torch.tensor(emb)) for path, emb in data]
    #with open(path, "rb") as f:
    #    return pickle.load(f)
