# Cloud Sentinel

**Policy-based cloud resource auditing and remediation** — Terraform, LocalStack, Python. Built for compliance checks (encryption, tagging) and cost control (orphan cleanup).

---

## What it does

- **Terraform** provisions only **compliant** EBS volumes (desired state). Non-compliant “junk” is **not** in Terraform — in real life it’s drift or legacy; for demo we **seed** it with a script.
- **Sentinel** audits all volumes, finds policy violations (e.g. Production unencrypted, missing Owner tag), writes `audit_report.json`.
- **Viewer** shows the report in the CLI; **Notifier** sends it to console (and optional Slack/Teams).
- **Janitor** deletes non-compliant volumes with confirmation. Because junk isn’t in Terraform, **it stays deleted** — no `terraform apply` will bring it back.

So: apply = compliant only → (optional) seed demo junk → audit → notify → remediate → junk is gone for good.

---

## Tech stack

| Layer        | Tech |
|-------------|------|
| IaC         | Terraform (AWS provider, LocalStack) |
| Config      | Ansible (optional deploy/run playbook) |
| Runtime     | Python 3.9+ (boto3) |
| Local AWS   | LocalStack (Docker) |
| Notifications | Console + optional Slack/Teams webhooks |

---

## Prerequisites

- **Docker** and **Docker Compose** (for LocalStack)
- **Terraform** ≥ 1.x ([install](https://developer.hashicorp.com/terraform/downloads))
- **Python** 3.9+ and `pip`

---

## Quick start

*(On Windows, use the steps below in PowerShell or WSL; `make` is optional.)*

```bash
# 1. Start LocalStack
cd infra && docker compose up -d
# Wait ~10s for readiness, then:

# 2. Terraform: compliant resources only (desired state)
terraform init && terraform apply -auto-approve

# 3. Install Python deps (from repo root)
pip install -r requirements.txt

# 4. (Demo only) Seed non-compliant volumes so Sentinel has something to find
python seed_demo_junk.py

# 5. Run audit → audit_report.json
python sentinel.py

# 6. View report
python viewer.py

# 7. Notify (console; set SLACK_WEBHOOK_URL / TEAMS_WEBHOOK_URL for webhooks)
cd ../bot && python notifier.py

# 8. Remediate: delete non-compliant volumes (confirmation required). They stay gone.
cd ../infra && python janitor.py <volume-id>
```

---

## Project layout

```
├── README.md
├── requirements.txt
├── .env.example
├── infra/
│   ├── docker-compose.yml   # LocalStack
│   ├── main.tf, variables.tf, outputs.tf
│   ├── sentinel.py, viewer.py, janitor.py, seed_demo_junk.py
├── ansible/
│   ├── playbook.yml        # Optional: install deps + run sentinel
│   └── inventory.yml
└── bot/
    └── notifier.py          # Alerts (console + optional Slack/Teams)
```

---

## Configuration

- Copy `.env.example` to `.env` and set:
  - `LOCALSTACK_ENDPOINT`, `AWS_*` for local runs.
  - `SENTINEL_REPORT_PATH` if the report is not under `infra/`.
  - `SLACK_WEBHOOK_URL` or `TEAMS_WEBHOOK_URL` for webhook alerts (optional).
- Terraform: use `terraform.tfvars` or env vars for `aws_*` in real AWS (see `variables.tf`).

---

## CI/CD

- `.github/workflows/ci.yml`: Terraform `fmt` + `validate`, Python lint, and optional sentinel run.
- Run locally: `terraform fmt -check -recursive`, `terraform validate`, `ruff check infra bot`.

---

## Why junk isn’t in Terraform

If non-compliant volumes were defined in Terraform, deleting them with Janitor would be pointless: the next `terraform apply` would recreate them. Here, **only compliant resources are in Terraform**. Junk is either real drift (other teams, mistakes) or, for demo, created by `seed_demo_junk.py`. Sentinel finds it, Janitor removes it, and it stays removed.

**Note:** Terraform does not list or “see” resources it doesn’t manage. So `terraform plan` will show “No changes” even if junk volumes still exist. Use **Sentinel** (and viewer/notifier) to detect and report those; Terraform only ensures the compliant resources are present and correct.

---

## Policies (Sentinel)

1. **Production volumes** must be **encrypted** (flagged as HIGH risk if not).
2. **All volumes** must have an **Owner** tag (MEDIUM risk if missing).
3. Report includes estimated cost impact for non-compliant resources.

---

## Highlights

- **IaC**: Terraform with variables and outputs; works with LocalStack or real AWS.
- **Policy as code**: Automated checks for encryption and tagging; machine-readable report for automation.
- **Safe remediation**: Confirmation-based cleanup (Janitor) for change-control workflows.
- **Observability**: Optional Slack/Teams webhooks for alerting integration.
- **CI**: GitHub Actions for Terraform validate/fmt and Python lint; optional end-to-end audit job.

---

## License

MIT.
