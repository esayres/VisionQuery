from app.embedding import load_paths
from app.faissManager import load_or_create_index, search_index
import subprocess
import shutil
import sys

def open_in_gwenview(results):
    if not sys.platform.startswith("linux"):
        return False
    gwenview = shutil.which("gwenview")
    if not gwenview:
        return False
    image_paths = [path for path, _ in results if path]
    if not image_paths:
        return False
    subprocess.Popen([gwenview, *image_paths])
    return True

def search(query, model, top_k=50):
    index = load_or_create_index()
    paths = load_paths()

    query_embedding = model.encode_text(query)
    scores, indices = search_index(index, query_embedding, top_k)

    results = []
    for score, idx in zip(scores, indices):
        if idx == -1:  # FAISS returns -1 for empty slots
            continue
        if idx < len(paths):
            results.append((paths[idx], float(score)))

    return results