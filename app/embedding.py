from PIL import Image # type: ignore
import os
import pickle

def encode_images(folder_path, model):
    embeddings = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(root, file)

                try:
                    image = Image.open(path).convert("RGB")
                    emb = model.encode_image(image)
                    embeddings.append((path, emb))
                except Exception as e:
                    print(f"Skipping {path}: {e}")

    return embeddings


def save_embeddings(embeddings, path="data/embeddings.pkl"):
    with open(path, "wb") as f:
        pickle.dump(embeddings, f)


def load_embeddings(path="data/embeddings.pkl"):
    with open(path, "rb") as f:
        return pickle.load(f)
