import torch # type: ignore
import subprocess
import shutil
import sys

# For my own use, I want to be able to open the results in gwenview, so i can quickly scroll through them. you can replace with any image viewer you like 
def open_in_gwenview(results):
    if not sys.platform.startswith("linux"): # if os is not Linux, return False
        return False

    gwenview = shutil.which("gwenview") # if gwenview is not installed, return False
    if not gwenview:
        return False

    image_paths = []

    for path, _ in results:
        if path:
            image_paths.append(path)

    if not image_paths: # if no valid image paths, return False
        return False

    subprocess.Popen([gwenview, *image_paths]) # open images in gwenview
    return True
        


def search(query, model, embeddings, top_k=20):
    # Turn the text query into an embedding/vector so it can be compared against the image embeddings.
    query_embedding = model.encode_text(query)
    results = []

    # Compare the query embedding to every saved image embedding.
    for path, image_embedding in embeddings:
        score = torch.matmul(query_embedding, image_embedding.T).item() # Compute similarity score between the text query and this image.
        results.append((path, score)) # Save both the path and its score so we can sort later.

    # Sort results from highest score to lowest score.
    # each_result is a tuple like: (path, score)
    def get_score(each_result):
        return each_result[1]

    results.sort(key=get_score, reverse=True)

    # Return only the top matches.
    return results[:top_k]