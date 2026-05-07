from app.metrics import score_distribution, query_consistency, score_gap, embedding_coherence

score_distribution([
    "a cheetah on a rock",
    "a red sports car",
    "a person smiling",
    "elephant with a laser eyes",  # nonsense baseline
])

query_consistency([
    ("a cheetah", "a big cat in the wild"),
    ("a red car", "a sports car on a road"),
    ("a cheetah", "a red sports car"),  # cross-category, should be 0.00
])

score_gap([
    "a cheetah on a rock",
    "a red sports car",
    "a person smiling",
    "elephant with a laser eyes",  # gap should be smallest for nonsense
])

embedding_coherence([
    "a cheetah on a rock",
    "a red sports car",
    "a person smiling",
    "elephant with a laser eyes",  # coherence should be lowest for nonsense
])

# something intresting for consistency, quantifer words dominate more than descriptive
#"Adding count quantifiers like 'three' to a query reduced retrieval consistency from Jaccard 0.54 to 0.00, 
# indicating CLIP's text encoder is sensitive to quantifier words which can dominate the embedding direction away from the primary subject."