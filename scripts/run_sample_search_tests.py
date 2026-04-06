import json
from app.retrieval.vector_search_service import search_chunks

TEST_CASES = [
    ("user_1", "thermal design requirements", 3),
    ("user_2", "project schedule and milestones", 3),
    ("user_admin", "design requirements", 5),
]

def main():
    for user_id, query, top_k in TEST_CASES:
        print("=" * 80)
        print(f"user_id={user_id} | query={query} | top_k={top_k}")
        results = search_chunks(user_id=user_id, query=query, top_k=top_k)
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()