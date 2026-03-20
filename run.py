# use this as a main running script
# something esay like python run.py --query "a dog in snow"
import os
from models.clipModel import CLIPWrapper
from app.embedding import encode_images, save_embeddings, load_embeddings
from app.search import search, open_in_gwenview

IMAGE_FOLDER = "data/images"
EMBED_PATH = "data/embeddings.enc"


model = CLIPWrapper()

# Step 1: compute embeddings (run once)
#if os.path.exists(EMBED_PATH): # not perfect what if we add new images?
embeddings = load_embeddings(EMBED_PATH)
print("Loaded saved embeddings.")
#else: # now this doesnt need to save ever, listener will do the saving, this just needs to search for the img
#    print("Computing embeddings... this may take a while.")
#    embeddings = encode_images(IMAGE_FOLDER, model)
#    save_embeddings(embeddings, EMBED_PATH)
#    print("Computed and saved embeddings.")

# Step 2: query loop
while True:
    query = input("Enter search query: ")
    results = search(query, model, embeddings)

    print("\nTop matches:")
    for path, score in results:
        print(f"{path} (score: {score:.4f})")

    open_in_gwenview(results) # open in image viewer (optional)