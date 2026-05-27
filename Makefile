# CantinaIQ — convenience targets for examiners and curious developers.
#
# Quick start:
#   make setup     # install Python + Node deps
#   make demo      # full end-to-end demo: pipeline → reports → dashboard
#   make pipeline  # supercharged pipeline only
#   make reports   # regenerate markdown + HTML reports
#   make dashboard # build the dashboard SPA
#   make test      # run the Python test suite
#   make clean     # remove generated artifacts (keeps committed snapshots)
#
# Set OPENROUTER_API_KEY (or source .env.local) to enable real producer
# disambiguation. Without it the pipeline uses pass-1 results only.

.PHONY: setup pipeline reports dashboard demo test clean serve-dashboard brief help deploy redeploy
.DEFAULT_GOAL := help

PYTHON_DIR := supercharged
DASH_DIR   := dashboard

# Deploy target — overridable via `make deploy SSH_HOST=foo SSH_PATH=/var/www`
SSH_HOST   ?= clubventure
SSH_PATH   ?= /opt/apps/react-cantinaiq/site
TARBALL    := cantinaiq-dashboard.tar.gz

help:
	@printf "CantinaIQ — Slurpini Partner Intelligence\n\n"
	@printf "Common targets:\n"
	@printf "  make setup      Install all dependencies (Python + Node)\n"
	@printf "  make demo       Full pipeline + reports + dashboard build (≈ 30 s)\n"
	@printf "  make pipeline   Run the supercharged data pipeline\n"
	@printf "  make reports    Regenerate all reports\n"
	@printf "  make dashboard  Build the Vite dashboard SPA\n"
	@printf "  make serve-dashboard  Start the dashboard dev server on :5175\n"
	@printf "  make test       Run the Python test suite (137 tests)\n"
	@printf "  make deploy     Package current build and push to live server\n"
	@printf "  make redeploy   Pipeline + reports + dashboard + deploy (full chain)\n"
	@printf "  make clean      Remove generated artifacts\n\n"
	@printf "Inputs:\n"
	@printf "  Vivino-export.xlsx in supercharged/data/raw/\n"
	@printf "  OPENROUTER_API_KEY in env (optional — enables LLM disambiguation)\n"
	@printf "  FIRECRAWL_API_KEY  in env (optional — enables live enrichment + sustainability)\n\n"
	@printf "Deploy overrides:\n"
	@printf "  SSH_HOST=$(SSH_HOST)   SSH_PATH=$(SSH_PATH)\n"

setup:
	@echo "→ installing Python dependencies (uv)"
	cd $(PYTHON_DIR) && uv sync
	@echo "→ installing dashboard dependencies (npm)"
	cd $(DASH_DIR) && npm install

pipeline:
	@echo "→ running supercharged pipeline"
	cd $(PYTHON_DIR) && uv run cantinaiq run all

reports:
	@echo "→ rebuilding reports"
	cd $(PYTHON_DIR) && uv run cantinaiq report build
	cd $(PYTHON_DIR) && uv run cantinaiq evaluate producer-extraction
	cd $(PYTHON_DIR) && uv run cantinaiq bias
	cd $(PYTHON_DIR) && uv run cantinaiq anomaly --contamination 0.03
	cd $(PYTHON_DIR) && uv run cantinaiq bootstrap --n 200 --top 20

dashboard:
	@echo "→ building dashboard SPA"
	cd $(DASH_DIR) && npm run build

serve-dashboard:
	@echo "→ starting dashboard dev server on http://localhost:5175"
	cd $(DASH_DIR) && npm run dev

test:
	cd $(PYTHON_DIR) && uv run pytest

brief:
	@echo "→ rendering CantinaIQ Strategy Brief"
	"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
	  --headless --disable-gpu --no-pdf-header-footer --print-to-pdf-no-header \
	  --print-to-pdf=$(PYTHON_DIR)/docs/brief/brief.pdf --virtual-time-budget=5000 \
	  "file://$(CURDIR)/$(PYTHON_DIR)/docs/brief/brief.html"
	cp $(PYTHON_DIR)/docs/brief/brief.pdf CantinaIQ-in-Practice.pdf
	@echo "✓ CantinaIQ-in-Practice.pdf (4.2 MB, 12 pages)"

demo: pipeline reports dashboard
	@printf "\n\033[32m✓ Demo built.\033[0m\n"
	@printf "  Reports:    $(PYTHON_DIR)/reports/generated/\n"
	@printf "  Dashboard:  $(DASH_DIR)/dist/index.html\n"
	@printf "\nQuick reads:\n"
	@printf "  Executive summary:   $(PYTHON_DIR)/reports/generated/executive-summary.md\n"
	@printf "  Findings one-pager:  $(PYTHON_DIR)/reports/generated/findings-one-pager.html\n"
	@printf "  Bias quantification: $(PYTHON_DIR)/reports/generated/bias-report.md\n"
	@printf "  Bootstrap CIs:       $(PYTHON_DIR)/reports/generated/bootstrap-ci.md\n"
	@printf "\nServe dashboard:    make serve-dashboard\n"

clean:
	rm -rf $(PYTHON_DIR)/reports/generated/* \
	       $(PYTHON_DIR)/data/interim/* \
	       $(PYTHON_DIR)/data/processed/* \
	       $(PYTHON_DIR)/data/exports/* \
	       $(PYTHON_DIR)/data/runs/2026-* \
	       $(DASH_DIR)/dist
	@echo "✓ cleaned (kept config snapshots + raw data + reference cache)"

# Deploy current dashboard build to the live server.
# Creates a timestamped backup on the server before extracting.
deploy:
	@echo "→ packaging dashboard build"
	@./deploy/package.sh
	@echo "→ uploading tarball to $(SSH_HOST):/tmp/"
	@scp $(TARBALL) $(SSH_HOST):/tmp/
	@echo "→ backing up + extracting on server"
	@ssh $(SSH_HOST) 'set -e; \
	  STAMP=$$(date +%Y%m%d-%H%M); \
	  echo "  backup → /tmp/cantinaiq-site-backup-$${STAMP}.tar.gz"; \
	  tar -czf /tmp/cantinaiq-site-backup-$${STAMP}.tar.gz -C $(SSH_PATH) .; \
	  tar --overwrite -xzf /tmp/$(TARBALL) -C $(SSH_PATH) 2>&1 | grep -v "LIBARCHIVE.xattr" || true; \
	  echo "  ✓ extracted to $(SSH_PATH)"'
	@printf "\n\033[32m✓ Live at https://cantinaiq.clubventure.nl/\033[0m\n"
	@printf "  Rollback: ssh $(SSH_HOST) 'tar -xzf /tmp/cantinaiq-site-backup-<STAMP>.tar.gz -C $(SSH_PATH)'\n"

# Full chain — re-run pipeline, regenerate reports, rebuild dashboard, deploy.
# Use after editing supercharged/data/raw/Vivino-export.xlsx or config.
redeploy: pipeline reports dashboard deploy
	@printf "\033[32m✓ Full redeploy complete.\033[0m\n"
