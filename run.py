# use this as a main running script
# something esay like python run.py --query "a dog in snow"
import os
from models.clipModel import CLIPWrapper
from app.search import search, open_in_gwenview

IMAGE_FOLDER = "data/images"


model = CLIPWrapper() # takes alot of ram when you have alot of photos (300k photos was roughly 7-8gb of ram for embeddings)

# Step 1: compute embeddings (run once)

# Step 2: query loop 
# LETS ADD A TIME OUT FEATURE HERE, SO IF THE USER DOESNT ENTER A QUERY FOR A WHILE (5-10 mins), IT EXITS THE PROGRAM
# IF USER SENTS A QUERY THEN IT RESETS THE TIMER
while True:
    query = input("Enter search query: ")
    results = search(query, model) # in search it justs to just load the embeddings from disk, it doesnt need to take them as an argument.

    print("\nTop matches:")
    for path, score in results:
        print(f"{path} (score: {score:.4f})")

    open_in_gwenview(results) # open in image viewer (optional)