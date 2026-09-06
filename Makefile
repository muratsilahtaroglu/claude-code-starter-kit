SHELL := /bin/bash  # the test target needs bash (pipefail); assumed at /bin/bash like everywhere mainstream
.PHONY: setup setup-dev lint test test-fast run lock audit team-clean team-status

setup:  ## Install pinned runtime deps with hash verification
	pip install --require-hashes -r requirements/base.lock

setup-dev:  ## Install dev tooling (pytest/ruff/...) with hash verification
	pip install --require-hashes -r requirements/dev.lock

lock:  ## Refresh both lock files from the .txt files
	pip-compile --generate-hashes -o requirements/base.lock requirements/base.txt
	pip-compile --generate-hashes -o requirements/dev.lock requirements/dev.txt

audit:  ## Check locked deps for known CVEs
	pip-audit -r requirements/base.lock
	pip-audit -r requirements/dev.lock

lint:  ## Lint + format-check with ruff (config in pyproject.toml)
	ruff check .
	ruff format --check .

test:  ## Run the full test suite (auto-log: reports/tests/<date>/<time>-pytest.log)
	@d="reports/tests/$$(date +%F)"; mkdir -p "$$d"; log="$$d/$$(date +%H%M%S)-pytest.log"; \
	echo "# test run $$(date '+%F %T') · commit $$(git rev-parse --short HEAD 2>/dev/null || echo none) · branch $$(b=$$(git branch --show-current 2>/dev/null); echo $${b:-none})" >> "$$log"; \
	set -o pipefail; pytest tests/ 2>&1 | tee -a "$$log"

test-fast:  ## Commit-time subset (seconds, not minutes) — wire it into pre-commit (see .pre-commit-config.yaml)
	# Measured on a live project: `make test` had produced no log for 11 days and .git/hooks was
	# empty — a 10-40 commit regression window. Keep this to the tests that run in seconds
	# (`-m "not slow"` needs a `slow` marker in pyproject.toml); the full suite stays `make test`.
	pytest tests/unit -x -m "not slow"

team-clean:  ## Agent team: SHOW the twin table (one session-id, several processes) — never kills
	# A reconnect (sleep · tunnel · second machine) resumes the SAME session id in a NEW process, so
	# twins accumulate on their own; the NEWEST is live, older ones are lossless leftovers (rules
	# §10.42, docs/steering.md). This prints the resolver's table and the WINDOWS to close. It runs
	# no `kill`: pids are recycled, a frozen `kill <pid>` is a security error — you close the windows.
	@python3 .claude/team-addresses.py || true

team-status:  ## Agent team: what is each lane doing RIGHT NOW (each lane's one-line status file)
	# The board shows open vs delivered; "being worked on" has no state there. Each worker writes ONE
	# line to its own `reports/team/<name>/status` (single writer — §10.42), this prints them all.
	@for f in reports/team/*/status; do [ -f "$$f" ] && printf '%-18s %s\n' "$$(basename "$$(dirname "$$f")")" "$$(head -1 "$$f")"; done; true

run:  ## <wire up the app entrypoint>
	@echo "TODO: configure run command"
