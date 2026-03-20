# use this as a main running script
# something esay like python run.py --query "a dog in snow"
import os
from models.clipModel import CLIPWrapper
from app.search import search, open_in_gwenview

IMAGE_FOLDER = "data/images"


model = CLIPWrapper()

# Step 1: compute embeddings (run once)
#if os.path.exists(EMBED_PATH): # not perfect what if we add new images?
#else: # now this doesnt need to save ever, listener will do the saving, this just needs to search for the img
#    print("Computing embeddings... this may take a while.")
#    embeddings = encode_images(IMAGE_FOLDER, model)
#    save_embeddings(embeddings, EMBED_PATH)
#    print("Computed and saved embeddings.")

# Step 2: query loop
while True:
    query = input("Enter search query: ")
    results = search(query, model) # in search it justs to just load the embeddings from disk, it doesnt need to take them as an argument.

    print("\nTop matches:")
    for path, score in results:
        print(f"{path} (score: {score:.4f})")

    open_in_gwenview(results) # open in image viewer (optional)