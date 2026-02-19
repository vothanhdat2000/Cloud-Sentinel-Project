# Cloud Sentinel - convenience targets (run from repo root)
# Requires: Docker, Terraform, Python 3.9+, pip

.PHONY: up down plan apply seed audit view notify clean lint

# Start LocalStack
up:
	cd infra && docker compose up -d

# Stop LocalStack
down:
	cd infra && docker compose down

# Terraform plan (LocalStack must be up)
plan:
	cd infra && terraform init -backend=false && terraform plan -input=false

# Terraform apply
apply:
	cd infra && terraform init -backend=false && terraform apply -auto-approve -input=false

# Seed non-compliant volumes for demo (so Sentinel has something to find)
seed:
	cd infra && python seed_demo_junk.py

# Run policy audit (requires apply; use seed for demo issues)
audit:
	cd infra && python sentinel.py

# View last audit report
view:
	cd infra && python viewer.py

# Send notification (console + webhooks if configured)
notify:
	python bot/notifier.py

# Full pipeline: up -> apply -> seed demo junk -> audit -> view -> notify
run: up
	@echo "Waiting for LocalStack..."
	@sleep 15
	$(MAKE) apply
	$(MAKE) seed
	$(MAKE) audit
	$(MAKE) view
	$(MAKE) notify

# Clean generated files
clean:
	rm -f infra/audit_report.json
	cd infra && terraform destroy -auto-approve -input=false 2>/dev/null || true

# Lint (install ruff: pip install ruff)
lint:
	ruff check infra bot && ruff format --check infra bot
