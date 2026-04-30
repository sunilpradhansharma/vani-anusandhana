"""
Run after `make setup` to confirm the environment is fully working.
Exits 0 on success, 1 on any failure.
"""
import sys

failures = []


def check(label: str, fn):
    try:
        fn()
        print(f"  ✅ {label}")
    except Exception as e:
        print(f"  ❌ {label}: {e}")
        failures.append(label)


print("\n── Checking Python imports ─────────────────────────────────────────")

check("mlx_whisper", lambda: __import__("mlx_whisper"))
check("yt_dlp", lambda: __import__("yt_dlp"))
check("sentence_transformers", lambda: __import__("sentence_transformers"))
check("FlagEmbedding", lambda: __import__("FlagEmbedding"))
check("qdrant_client", lambda: __import__("qdrant_client"))
check("fastapi", lambda: __import__("fastapi"))
check("uvicorn", lambda: __import__("uvicorn"))
check("tqdm", lambda: __import__("tqdm"))
check("rapidfuzz", lambda: __import__("rapidfuzz"))

print("\n── Checking Qdrant connection ──────────────────────────────────────")


def check_qdrant():
    from qdrant_client import QdrantClient
    client = QdrantClient(host="localhost", port=6333)
    info = client.get_collections()
    print(f"       collections: {[c.name for c in info.collections]}")


check("Qdrant at localhost:6333", check_qdrant)

print("\n── Loading bge-m3 (first run downloads ~2 GB — be patient) ────────")


def check_bge_m3():
    from FlagEmbedding import BGEM3FlagModel
    model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
    result = model.encode(["test"], batch_size=1, max_length=16)
    assert "dense_vecs" in result, "dense_vecs missing from output"
    dim = len(result["dense_vecs"][0])
    print(f"       dense vector dim: {dim}")
    assert dim == 1024, f"expected 1024, got {dim}"


check("bge-m3 loads and encodes", check_bge_m3)

print()
if failures:
    print(f"❌  {len(failures)} check(s) failed: {', '.join(failures)}")
    print("   Fix the issues above, then re-run: python verify_setup.py\n")
    sys.exit(1)
else:
    print("✅  environment ready — proceed to Prompt 1\n")
    sys.exit(0)
