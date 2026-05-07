# migrate.py — run once
from app.embedding import load_embeddings  # old version before your changes
from app.faissManager import load_or_create_index, add_embeddings_to_index, save_index
from app.encryption import EncryptionManager
import torch

old_embeddings = load_embeddings()  # loads old (path, tensor) pairs
index = load_or_create_index()
add_embeddings_to_index(index, old_embeddings)
save_index(index)

pathManager = EncryptionManager("embedding_paths")
pathManager.file_contents = [path for path, _ in old_embeddings]
pathManager.save_file_contents()
print(f"Migrated {len(old_embeddings)} embeddings to FAISS.")