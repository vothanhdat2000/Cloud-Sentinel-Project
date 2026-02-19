# bot/notifier.py - Compliance report: console + optional Slack/Teams webhooks
import json
import os
import sys

REPORT_PATH = os.environ.get(
    "SENTINEL_REPORT_PATH",
    os.path.join(os.path.dirname(__file__), "..", "infra", "audit_report.json"),
)
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
TEAMS_WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_URL", "").strip()


def load_report():
    if not os.path.exists(REPORT_PATH):
        return None, "No audit report found. Run sentinel.py first."
    try:
        with open(REPORT_PATH, "r") as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"Invalid report JSON: {e}"


def format_console(report_data):
    lines = [
        "",
        "=" * 70,
        "           CLOUD SENTINEL - INFRASTRUCTURE COMPLIANCE REPORT          ",
        "=" * 70,
        f"{'RESOURCE ID':<25} | {'RISK':<8} | {'IMPACT':<15}",
        "-" * 70,
    ]
    for item in report_data:
        res_id = item.get("VolumeID", item.get("ResourceID", "N/A"))
        risk = item.get("Risk", "N/A")
        impact = (item.get("Impact") or "").split(":")[-1].strip()
        reason = item.get("Reason", "")
        lines.append(f"{res_id:<25} | {risk:<8} | {impact:<15}")
        lines.append(f"REASON: {reason}")
        lines.append("-" * 70)
    lines.append(f"SUMMARY: {len(report_data)} non-compliant resource(s). Run janitor.py for remediation.")
    lines.append("=" * 70 + "")
    return "\n".join(lines)


def send_slack(report_data):
    if not SLACK_WEBHOOK_URL:
        return
    try:
        import requests
        text = f"*Cloud Sentinel* – {len(report_data)} non-compliant resource(s).\n"
        for item in report_data:
            text += f"• `{item.get('VolumeID', 'N/A')}` [{item.get('Risk')}] {item.get('Reason', '')}\n"
        resp = requests.post(SLACK_WEBHOOK_URL, json={"text": text}, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[WARN] Slack notification failed: {e}", file=sys.stderr)


def send_teams(report_data):
    if not TEAMS_WEBHOOK_URL:
        return
    try:
        import requests
        facts = [{"name": "Count", "value": str(len(report_data))}]
        for i, item in enumerate(report_data[:10]):
            facts.append({
                "name": item.get("VolumeID", "N/A"),
                "value": f"{item.get('Risk')}: {item.get('Reason', '')[:80]}",
            })
        payload = {
            "@type": "MessageCard",
            "themeColor": "FF0000",
            "title": "Cloud Sentinel – Compliance Report",
            "summary": f"{len(report_data)} non-compliant resource(s).",
            "sections": [{"facts": facts}],
        }
        resp = requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[WARN] Teams notification failed: {e}", file=sys.stderr)


def send_notification():
    report_data, err = load_report()
    if err:
        print(f"[LOG] {err}")
        return

    if not report_data:
        print("[LOG] Infrastructure compliant. No issues detected.")
        return

    print(format_console(report_data))
    send_slack(report_data)
    send_teams(report_data)


if __name__ == "__main__":
    send_notification()
