import os
import numpy as np
from app.faissManager import load_or_create_index, search_index, faiss
from app.embedding import load_paths
from models.clipModel import CLIPWrapper
from collections import Counter

def dataset_class_distribution(images_dir="data/images", top_n=10):
    """Count images per subfolder (proxy for class distribution)."""
    counts = Counter()
    for root, dirs, files in os.walk(images_dir):
        images = [f for f in files if f.lower().endswith((".jpg", ".png", ".jpeg"))]
        if images:
            class_name = os.path.basename(root)
            counts[class_name] += len(images)

    print(f"\nDataset distribution (top {top_n} classes):")
    for cls, count in counts.most_common(top_n):
        print(f"  {cls:<30} {count} images")
    
    total = sum(counts.values())
    print(f"\n  Total classes: {len(counts)}")
    print(f"  Total images:  {total}")
    print(f"  Mean per class: {total / len(counts):.1f}")



def score_distribution(queries: list[str]):
    """
    For each query, print the score distribution of top-k results.
    Tells you if scores are meaningful or bunched together.
    """
    model = CLIPWrapper()
    index = load_or_create_index()
    paths = load_paths()

    for query in queries:
        query_emb = model.encode_text(query)
        scores, indices = search_index(index, query_emb, top_k=10)
        valid_scores = [s for s, i in zip(scores, indices) if i != -1]

        print(f"\nQuery: '{query}'")
        print(f"  Top score:    {max(valid_scores):.4f}")
        print(f"  Bottom score: {min(valid_scores):.4f}")
        print(f"  Mean:         {np.mean(valid_scores):.4f}")
        print(f"  Std dev:      {np.std(valid_scores):.4f}") # low std dev = scores are bunched = bad signal
    
    del model


def query_consistency(query_pairs: list[tuple[str, str]], top_k=10):
    """
    Given pairs of semantically similar queries, measure how much their
    top-k results overlap. High overlap = consistent retrieval.

    Example pairs:
        [("a dog in snow", "dog playing in snow"),
         ("red fruit", "apple on table")]
    """
    model = CLIPWrapper()
    index = load_or_create_index()
    paths = load_paths()

    for q1, q2 in query_pairs:
        emb1 = model.encode_text(q1)
        emb2 = model.encode_text(q2)

        _, indices1 = search_index(index, emb1, top_k)
        _, indices2 = search_index(index, emb2, top_k)

        set1 = set(indices1[indices1 != -1])
        set2 = set(indices2[indices2 != -1])

        overlap = len(set1 & set2)
        jaccard = overlap / len(set1 | set2) if set1 | set2 else 0

        print(f"\nQuery 1: '{q1}'")
        print(f"Query 2: '{q2}'")
        print(f"  Overlapping results: {overlap}/{top_k}")
        print(f"  Jaccard similarity:  {jaccard:.2f}") # 1.0 = identical results, 0.0 = no overlap

    del model


def top_k_precision(labeled_queries: list[dict], top_k=10):
    """
    For queries where you KNOW what a relevant result looks like,
    measure how many top-k results are actually relevant.

    labeled_queries format:
        [{"query": "a dog", "relevant_keywords": ["dog", "puppy", "hound"]}, ...]
    
    This uses filename matching as a proxy for relevance since you 
    don't have human-labeled ground truth.
    """
    model = CLIPWrapper()
    index = load_or_create_index()
    paths = load_paths()

    for item in labeled_queries:
        query = item["query"]
        keywords = [k.lower() for k in item["relevant_keywords"]]

        query_emb = model.encode_text(query)
        scores, indices = search_index(index, query_emb, top_k)

        hits = 0
        for idx in indices:
            if idx == -1:
                continue
            filename = paths[idx].lower()
            if any(kw in filename for kw in keywords):
                hits += 1

        precision = hits / top_k
        print(f"\nQuery: '{query}'")
        print(f"  Relevant results in top-{top_k}: {hits}/{top_k}")
        print(f"  Precision@{top_k}: {precision:.2f}")

    del model


def score_gap(queries: list[str], top_k=10):
    """
    Compares top result score vs mean of remaining results.
    A large gap means CLIP is genuinely confident in top results.
    A small gap means results are essentially random.
    """
    model = CLIPWrapper()
    index = load_or_create_index()
    paths = load_paths()

    for query in queries:
        query_emb = model.encode_text(query)
        # fetch more than top_k to compare top vs rest
        scores, indices = search_index(index, query_emb, top_k=50)
        valid_scores = scores[indices != -1]

        top_scores = valid_scores[:top_k]
        rest_scores = valid_scores[top_k:]

        gap = np.mean(top_scores) - np.mean(rest_scores)

        print(f"\nQuery: '{query}'")
        print(f"  Top-{top_k} mean score: {np.mean(top_scores):.4f}")
        print(f"  Rest mean score:      {np.mean(rest_scores):.4f}")
        print(f"  Score gap:            {gap:.4f}")  # bigger = more confident retrieval

    del model


def embedding_coherence(queries: list[str], top_k=10):
    """
    Measures how visually similar the top-k results are to each other.
    High coherence = results belong to the same visual category.
    Low coherence = results are visually scattered/random.
    """
    model = CLIPWrapper()
    index = load_or_create_index()
    paths = load_paths()
    DIMENSION = 512

    for query in queries:
        query_emb = model.encode_text(query)
        scores, indices = search_index(index, query_emb, top_k)
        valid_indices = indices[indices != -1]

        # reconstruct the vectors from the index for the top-k results
        result_vectors = np.zeros((len(valid_indices), DIMENSION), dtype="float32")
        for i, idx in enumerate(valid_indices):
            index.reconstruct(int(idx), result_vectors[i])

        # measure pairwise cosine similarity between all result vectors
        faiss.normalize_L2(result_vectors)
        similarity_matrix = result_vectors @ result_vectors.T

        # average of upper triangle (excluding diagonal) = mean pairwise similarity
        upper = similarity_matrix[np.triu_indices(len(result_vectors), k=1)]
        coherence = np.mean(upper)

        print(f"\nQuery: '{query}'")
        print(f"  Embedding coherence: {coherence:.4f}")  # 1.0 = all identical, 0.0 = completely scattered

    del model