# VisionQuery

VisionQuery is a semantic image search tool that lets users search a personal image collection using natural language instead of fixed labels or filenames. By using CLIP embeddings, the project maps both images and text into a shared vector space, enabling queries like `"a dog in snow"` or `"red fruit on a table"` to retrieve the most relevant images with no manual tagging required.

This project was built because I wanted a better way to search through images on my own computer, and I was interested in building that system myself. It became a practical tool while learning more about multimodal AI, semantic search, and retrieval system design.

---

## Features

- Natural language image search using CLIP (zero-shot, no labels needed)
- FAISS HNSW index for O(log n) approximate nearest-neighbor search
- Real-time file watching (new images are embedded automatically in the background)
- AES-GCM encrypted storage for image embeddings and file paths
- Chunked embedding storage to handle large datasets without overflow errors
- Recursively scans nested folders and external directories
- Evaluated with label-free retrieval metrics (score gap, embedding coherence, query consistency)

---

## How It Works

1. **Encode images** — every image is converted into a 512-dimensional vector using CLIP and added to a FAISS index
2. **Encode query** — a natural language query is embedded into the same vector space
3. **Search** — FAISS retrieves the nearest image vectors to the query using inner product similarity
4. **Decrypt and return** — an encrypted path list maps FAISS result indices back to file paths on disk

Because CLIP embeds text and images into a shared space, VisionQuery retrieves semantically relevant images without relying on filenames or folder names.

---

## Retrieval Evaluation

VisionQuery was evaluated using label-free metrics suited to a diverse, unlabeled dataset.

### Score Gap
Measures how much top-k results stand out from the rest of the index. A larger gap means CLIP is confidently separating relevant results from irrelevant ones.

| Query | Score Gap |
|---|---|
| a person smiling | 0.0226 |
| a red sports car | 0.0172 |
| a cheetah on a rock | 0.0145 |
| green hand with orange eye *(nonsense baseline)* | 0.0092 |

The nonsense query consistently produces the smallest gap, confirming the system discriminates meaningfully between real and garbage input.

### Embedding Coherence
Measures how visually similar the top-k results are to each other. High coherence means results belong to the same visual category.

| Query | Coherence |
|---|---|
| a cheetah on a rock | 0.7571 |
| green hand with orange eye *(nonsense)* | 0.7436 |
| a red sports car | 0.7261 |
| a person smiling | 0.6468 |

Person smiling scores lowest, expected, since human expressions are visually diverse by nature. The nonsense query still returns a visually coherent cluster, demonstrating a known CLIP behavior: it always finds *something* that matches, even for meaningless input.

### Query Consistency (Jaccard Similarity)
Measures overlap between top-k results for semantically similar queries. Also tests cross-category separation.

| Query Pair | Jaccard |
|---|---|
| "a cheetah" vs "a big cat in the wild" | 0.25 |
| "a red car" vs "a sports car on a road" | 0.11 |
| "a cheetah" vs "a red sports car" *(cross-category)* | 0.00 |

Cross-category separation is confirmed. Within-category overlap is lower on a large diverse dataset, which is expected. two similar queries pull different valid subsets from a large class pool.

### Quantifier Sensitivity Finding
A specific failure mode was identified: adding count words to a query significantly shifts CLIP's embedding direction away from the primary subject.

| Query Pair | Jaccard |
|---|---|
| "strawberries" vs "strawberries in a bowl" | 0.54 |
| "three strawberries" vs "strawberries in a bowl" | 0.00 |

**Recommendation:** avoid count words like "three" or "a pair of" in queries. Describe the subject and scene instead.

---

## Usage

**Place images inside the data folder:**
```
visionquery/
└── data/
    └── images/
```

Nested folders are supported:
```
data/images/dataset1/animals/cheetah.jpg
data/images/dataset2/fruits/apple.png
```

**Or list external directories in a text file (one path per line):**
```
data/directories.txt
---
/home/username/Photos/
/run/media/username/Drive/pictures/
```

The program recursively scans all listed directories for images.

**Then run:**
```bash
python app/listener.py   # scans for new images and builds the FAISS index
python run.py            # start the search interface
```

---

## Installation

```bash
git clone https://github.com/yourusername/visionquery.git
cd visionquery
pip install -r requirements.txt
```

Or manually:
```bash
pip install torch torchvision transformers pillow keyring watchdog cryptography faiss-cpu
```

---

## Tech Stack

- **Python**
- **PyTorch**
- **CLIP** (Contrastive Language–Image Pretraining via Hugging Face Transformers)
- **FAISS** — approximate nearest-neighbor search with HNSW index
- **Pillow** — image loading and preprocessing
- **Keyring + cryptography** — AES-GCM encryption for embeddings and paths
- **Watchdog** — real-time filesystem monitoring

---

## Project Structure

```
visionquery/
│
├── models/
│   └── clipModel.py          # Loads CLIP, encodes images and text
│
├── app/
│   ├── embedding.py          # Encodes images, manages FAISS index and encrypted path list
│   ├── encryption.py         # AES-GCM encrypted chunked storage
│   ├── faissManager.py       # FAISS index creation, search, and persistence
│   ├── listener.py           # Startup scan + real-time watchdog for new images
│   ├── search.py             # Query encoding and retrieval
│   └── metrics.py            # Label-free retrieval evaluation
│
├── data/
│   ├── images/               # Image dataset (nested folders supported)
│   ├── faiss.index           # HNSW vector index (created on first run)
│   ├── directories.txt       # Optional: external directories to scan
│   └── *.enc                 # Encrypted path list and seen-files chunks
│
├── evaluation.py             # Runs retrieval evaluation metrics
├── run.py                    # Main search entry point
├── requirements.txt
└── README.md
```

---

## Known Limitations

- All FAISS index vectors are held in memory during search — RAM usage scales with dataset size
- CLIP is sensitive to quantifier words ("three", "a pair of") which can dominate query embeddings
- Embedding new images is single-threaded; large initial scans are slow
- FAISS index and encrypted path list must stay in sync — deleting one without the other requires a full rebuild

---

## Future Work

- Batched multi-threaded image encoding for faster initial indexing
- FAISS IVF index for reduced memory usage on very large datasets (100k+ images)
- Query preprocessing to strip or normalize quantifier words before embedding
- Simple UI for browsing results instead of terminal output