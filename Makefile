.PHONY: setup qdrant-up qdrant-down clean-audio

# ── One-time setup ─────────────────────────────────────────────────────────────
setup:
	@echo "→ Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "→ Pulling Qdrant Docker image..."
	docker pull qdrant/qdrant
	@echo "→ Starting Qdrant..."
	docker compose up -d
	@echo "→ Verifying environment..."
	python verify_setup.py

# ── Qdrant lifecycle ───────────────────────────────────────────────────────────
qdrant-up:
	docker compose up -d
	@echo "✅ Qdrant running on http://localhost:6333"

qdrant-down:
	docker compose down
	@echo "Qdrant stopped."

# ── Housekeeping ───────────────────────────────────────────────────────────────
clean-audio:
	@echo "Deleting data/audio/ contents..."
	rm -rf data/audio/*
	@echo "✅ Audio files deleted. Transcripts in data/transcripts/ are untouched."
