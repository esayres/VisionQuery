import faiss
import numpy as np
import os

INDEX_PATH = "data/faiss.index"
DIMENSION = 512  # CLIP embedding size

def load_or_create_index():
    if os.path.exists(INDEX_PATH):
        print("Loading existing FAISS index...")
        return faiss.read_index(INDEX_PATH)
    print("Creating new FAISS index...")
    # IndexFlatIP = Inner Product (cosine similarity, since CLIP embeddings are normalized)
    return faiss.IndexHNSWFlat(DIMENSION, 32, faiss.METRIC_INNER_PRODUCT) # HNSW with 32 neighbors for faster search

def save_index(index):
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

def add_embeddings_to_index(index, embeddings_list):
    """
    embeddings_list: list of (path, tensor) tuples — only the NEW ones
    Returns: the numpy array added, so callers can pair it with paths
    """
    if not embeddings_list:
        return None
    vectors = np.stack([emb.squeeze().cpu().numpy() for _, emb in embeddings_list]).astype("float32")
    faiss.normalize_L2(vectors)  # normalize for cosine similarity
    index.add(vectors)
    return vectors

def search_index(index, query_embedding, top_k=50):
    """
    query_embedding: a torch tensor of shape (512,)
    Returns: (scores, indices) numpy arrays
    """
    vector = query_embedding.squeeze().cpu().numpy().astype("float32")
    vector = vector.reshape(1, -1)
    faiss.normalize_L2(vector)
    scores, indices = index.search(vector, top_k)
    return scores[0], indices[0]