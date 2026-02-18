"""
Diagnostic script to understand recall regression.
Run with: python diagnose.py
"""

import json
import pickle
import re
from pathlib import Path


def load_ground_truth(path: str) -> list:
    with open(path) as f:
        data = json.load(f)
    return data["rag_questions"]


def load_index(path: str):
    with open(path, "rb") as f:
        return pickle.load(f)


def tokenize_old(text: str) -> list:
    """Old tokenizer - simple split"""
    return text.lower().split()


def tokenize_new(text: str) -> list:
    """New tokenizer - regex + stopwords"""
    text = text.lower()
    tokens = re.findall(r'\w+', text)
    stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}
    return [t for t in tokens if t not in stopwords]


print("=" * 60)
print("RAG DIAGNOSTIC REPORT")
print("=" * 60)

# 1. Check ground truth paths
print("\n1. GROUND TRUTH - Sample file paths:")
gt = load_ground_truth("datasets/AnsweredQuestions/dataset_docs_public.json")
gt_paths = set()
for q in gt[:5]:
    for s in q.get("sources", []):
        print(f"   GT path: {s['file_path']}")
        gt_paths.add(s['file_path'])

# 2. Check indexed paths
print("\n2. INDEX - Sample file paths:")
index_data = load_index("data/processed/bm25_index.pkl")
indexed_chunks = index_data['indexed_chunks']

sample_paths = set()
for chunk in indexed_chunks[:200]:
    sample_paths.add(chunk.chunk.file_path)

for p in list(sample_paths)[:5]:
    print(f"   IDX path: {p}")

# 3. Check path overlap
print("\n3. PATH MATCH CHECK:")
all_gt_paths = set()
for q in gt:
    for s in q.get("sources", []):
        all_gt_paths.add(s['file_path'])

all_idx_paths = set(c.chunk.file_path for c in indexed_chunks)

matched = all_gt_paths & all_idx_paths
print(f"   GT unique paths:    {len(all_gt_paths)}")
print(f"   Index unique paths: {len(all_idx_paths)}")
print(f"   Paths that match:   {len(matched)}")
print(f"   Paths NOT found:    {len(all_gt_paths - all_idx_paths)}")

if len(matched) == 0:
    print("\n   ❌ CRITICAL: NO PATHS MATCH! This is the bug.")
    print("   GT example:  ", list(all_gt_paths)[0])
    print("   IDX example: ", list(all_idx_paths)[0])
elif len(matched) < len(all_gt_paths) * 0.8:
    print(f"\n   ⚠️  WARNING: Only {len(matched)/len(all_gt_paths)*100:.0f}% of GT paths found in index!")
else:
    print(f"\n   ✅ {len(matched)/len(all_gt_paths)*100:.0f}% of GT paths found in index")

# 4. Tokenizer comparison on a real query
print("\n4. TOKENIZER COMPARISON:")
q = gt[0]
query = q["question"]
print(f"   Query: {query}")
print(f"   Old tokenizer: {tokenize_old(query)[:10]}")
print(f"   New tokenizer: {tokenize_new(query)[:10]}")

# 5. Check chunk count
print(f"\n5. CHUNK STATISTICS:")
print(f"   Total chunks:     {len(indexed_chunks)}")
py_chunks = sum(1 for c in indexed_chunks if c.chunk.file_path.endswith('.py'))
md_chunks = sum(1 for c in indexed_chunks if c.chunk.file_path.endswith('.md'))
print(f"   Python chunks:    {py_chunks}")
print(f"   Markdown chunks:  {md_chunks}")
print(f"   Other chunks:     {len(indexed_chunks) - py_chunks - md_chunks}")

# 6. Check if ground truth chunks would be found
print("\n6. GROUND TRUTH CHUNK COVERAGE:")
found = 0
not_found = 0
for q in gt[:20]:
    for src in q.get("sources", []):
        gt_path = src['file_path']
        gt_start = src['first_character_index']
        gt_end = src['last_character_index']

        # Check if any indexed chunk overlaps
        found_match = False
        for chunk in indexed_chunks:
            if chunk.chunk.file_path != gt_path:
                continue
            # Check 5% overlap
            overlap_start = max(chunk.chunk.first_character_index, gt_start)
            overlap_end = min(chunk.chunk.last_character_index, gt_end)
            overlap = max(0, overlap_end - overlap_start)
            gt_len = gt_end - gt_start
            if gt_len > 0 and overlap / gt_len >= 0.05:
                found_match = True
                break

        if found_match:
            found += 1
        else:
            not_found += 1
            print(f"   ❌ NOT COVERED: {gt_path} [{gt_start}:{gt_end}]")

print(f"\n   Covered: {found}, Not covered: {not_found}")
print(f"   Coverage: {found/(found+not_found)*100:.1f}%")
print("\n" + "=" * 60)
print("DONE. Check the output above for the root cause.")
print("=" * 60)
