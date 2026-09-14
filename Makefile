# lead_HS — operator entrypoint (v0.2.1). One target = one `leadhs` call;
# pipeline logic lives in the CLI (D21); make stays a thin wrapper.
# Parameters are make variables until M1 (committed config file).

.PHONY: help install doctor db-init db-status db-audit sources-load \
	sources-list setup probe-dry probe-single record report \
	report-publish probe census recon probe-recon test smoke test-net \
	probe-capability capability probe-landscape landscape \
	clean clobber frame sample acquire ingest parse analyze full
.DEFAULT_GOAL := help

PYTHON      ?= python3
DB          ?= data/leadhs.sqlite
MODE        ?= census
SAMPLE      ?= 5
SOURCE      ?=
REPORT_DIR  ?= data/report
PUBLISH_DIR ?= docs/report

export LEADHS_CONTACT
export LEADHS_DEBUG

LEADHS = leadhs --db $(DB)

help: ## self-documenting index
	@grep -hE '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
	  sed -E 's/^([a-zA-Z_-]+):.*## *(.*)$$/  \1  \2/' | sort

install: ## editable install into the active interpreter
	$(PYTHON) -m pip install -e .

doctor: ## environment preflight
	$(LEADHS) doctor

db-init: ## apply pending migrations (backup taken by default)
	$(LEADHS) db init

db-status: ## applied/pending migrations, row counts
	$(LEADHS) db status

db-audit: ## provenance rules R1–R9 + raw-store orphans
	$(LEADHS) db audit --unreferenced

sources-load: ## upsert register from src/leadhs/dict/sources.csv
	$(LEADHS) source load

sources-list: ## list registered sources
	$(LEADHS) source list

setup: install db-init sources-load doctor ## first-run: install + init + load + doctor (idempotent)

probe-dry: ## census plan; zero network
	$(LEADHS) probe run --all --dry-run

probe-single: ## probe one source (SOURCE=CS-1)
	$(LEADHS) probe run --source $(SOURCE) --mode $(MODE) --sample $(SAMPLE)

record: ## manual finding (SOURCE= METRIC= VALUE=|VALUE_TEXT= [UNIT=] [URL=] [NOTE=])
	$(LEADHS) probe record --source $(SOURCE) --metric $(METRIC) \
		$(if $(VALUE),--value $(VALUE)) \
		$(if $(VALUE_TEXT),--value-text "$(VALUE_TEXT)") \
		$(if $(UNIT),--unit $(UNIT)) \
		$(if $(URL),--url "$(URL)") \
		$(if $(NOTE),--note "$(NOTE)")

# Render history policy (v0.2.3 addendum): every render writes an
# immutable timestamped set probe-report.<UTC ts>.<ext> into
# $(REPORT_DIR) — one shared ts per run, nothing overwritten — and
# refreshes the unversioned "latest" copies for stable references.
# Publish history policy (v0.2.2 PHASE07 addendum): every publish stages
# the stable "latest" name AND an immutable timestamp-hash snapshot
# <stem>.<UTC ts>.<sha256-8>.<ext>, so unit republishes never overwrite
# a prior snapshot.
TS = $(shell date -u +%Y%m%d-%H%M%S)

report: ## render md/csv/json (timestamped set + latest copies) into $(REPORT_DIR)
	@mkdir -p $(REPORT_DIR)
	$(LEADHS) probe report --format md   --out $(REPORT_DIR)/probe-report.$(TS).md
	$(LEADHS) probe report --format csv  --out $(REPORT_DIR)/probe-report.$(TS).csv
	$(LEADHS) probe report --format json --out $(REPORT_DIR)/probe-report.$(TS).json
	cp $(REPORT_DIR)/probe-report.$(TS).md   $(REPORT_DIR)/probe-report.md
	cp $(REPORT_DIR)/probe-report.$(TS).csv  $(REPORT_DIR)/probe-report.csv
	cp $(REPORT_DIR)/probe-report.$(TS).json $(REPORT_DIR)/probe-report.json
	@echo "render set probe-report.$(TS).{md,csv,json} + latest copies in $(REPORT_DIR)"
report-publish: ## stage one report into $(PUBLISH_DIR) (WHICH=…; copies, never moves; + timestamp-hash snapshot)
	@test -n "$(WHICH)" || { echo "report-publish: set WHICH=path/to/report" >&2; exit 1; }
	@test -f "$(WHICH)" || { echo "report-publish: no such file $(WHICH)" >&2; exit 1; }
	@mkdir -p $(PUBLISH_DIR)
	@src=$$(readlink -f "$(WHICH)"); \
	dst_stem=$$(basename "$(WHICH)"); \
	stable=$$(printf '%s' "$$dst_stem" | sed -E 's/\.[0-9]{8}-[0-9]{6}(\.[A-Za-z0-9]+)$$/\1/'); \
	dst=$$(readlink -f "$(PUBLISH_DIR)")/$$stable; \
	if [ "$$src" != "$$dst" ]; then cp "$(WHICH)" "$(PUBLISH_DIR)/$$stable"; fi; \
	ts=$$(date -u +%Y%m%d-%H%M%S); \
	h=$$(sha256sum "$(WHICH)" | cut -c1-8); \
	base=$${stable%.*}; ext=$${stable##*.}; \
	if [ "$$base" = "$$ext" ]; then snap="$$stable.$$ts.$$h"; else snap="$$base.$$ts.$$h.$$ext"; fi; \
	cp "$(WHICH)" "$(PUBLISH_DIR)/$$snap"; \
	echo "staged $$stable into $(PUBLISH_DIR)/ (+ snapshot $$snap) — committing is explicit"

guard-%:
	@test "$(GO)" = "1" || { echo "$*: set GO=1 to confirm (GO=1 make $*)" >&2; exit 1; }

probe: guard-probe ## real census over all active sources (GO=1)
	$(LEADHS) probe run --all --mode $(MODE) --sample $(SAMPLE)

# e1/1A: the probe step inside a chain tolerates exactly exit 2 —
# expected blocked/failed sites must not abort report/audit (findings
# persist; any other failure still aborts the chain).
census: guard-census setup ## setup → probe → report → audit (GO=1; guard runs before setup)
	$(LEADHS) probe run --all --mode census --sample $(SAMPLE) || test $$? -eq 2
	$(MAKE) report
	$(MAKE) db-audit

probe-recon: guard-probe-recon ## recon sweep: robots-compliant, counts only (GO=1)
	$(LEADHS) probe run --all --mode recon

recon: guard-recon setup ## setup → recon → report → audit (GO=1)
	$(LEADHS) probe run --all --mode recon || test $$? -eq 2
	$(MAKE) report
	$(MAKE) db-audit

probe-capability: guard-probe-capability ## capability sweep: official register exports, shape inspect (GO=1)
	$(LEADHS) probe run --all --mode capability

capability: guard-capability setup ## setup → capability → report → audit (GO=1)
	$(LEADHS) probe run --all --mode capability || test $$? -eq 2
	$(MAKE) report
	$(MAKE) db-audit

# v0.2.2 (i20/fu5): the four-wave landscape run. WAVES="1 2 3 4" subset,
# BUDGET seconds per wave (default 3600), STAGING the staging-DB path.
WAVES   ?= 1 2 3
BUDGET  ?= 3600
STAGING ?= data/testdata.sqlite

probe-landscape: guard-probe-landscape ## landscape waves: probe run --wave W (GO=1)
	@for w in $(WAVES); do $(LEADHS) probe run --wave $$w --budget $(BUDGET) --staging-db $(STAGING) || test $$? -eq 2; done

landscape: guard-landscape setup ## setup → waves → report → audit (GO=1)
	@for w in $(WAVES); do $(LEADHS) probe run --wave $$w --budget $(BUDGET) --staging-db $(STAGING) || test $$? -eq 2; done
	$(MAKE) report
	$(MAKE) db-audit

test: ## offline suite (net/mdbtools markers deselected)
	$(PYTHON) -m pytest

smoke: ## end-to-end fixture smoke (2am-Friday test)
	$(PYTHON) -m pytest tests/test_cli_smoke.py

test-net: ## opt-in real-network checks
	$(PYTHON) -m pytest -m net

clean: ## remove caches and build artifacts
	rm -rf build/ .pytest_cache/ .benchmarks/
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

clobber: guard-clobber ## wipe local state (GO=1 + typed 'yes')
	@echo "clobber: this deletes the database and the raw store — type 'yes' to confirm"
	@read -r confirm; test "$$confirm" = "yes" || { echo "aborted"; exit 1; }
	rm -f "$(DB)" "$(DB)-wal" "$(DB)-shm"
	rm -rf data/raw data/backups $(REPORT_DIR)

# M1–M4 stubs — fail loudly with a pointer (strategy U6)
frame sample acquire ingest parse analyze full:
	@echo "error: '$@' is milestone-gated (M1–M4) — see 10_STRATEGY/ARCHITECTURE.md rollout" >&2
	@exit 1
