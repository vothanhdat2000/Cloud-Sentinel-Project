# viewer.py - CLI report viewer for Sentinel audit output
import json
import os

REPORT_FILE = os.environ.get("SENTINEL_REPORT_PATH", "audit_report.json")

def display_report():
    if not os.path.exists(REPORT_FILE):
        print("ERROR: No audit report found. Please run sentinel.py first.")
        return

    with open(REPORT_FILE, "r") as f:
        data = json.load(f)

    if not data:
        print("CLEAN: No non-compliant resources found in the report.")
        return

    print(f"{'RESOURCE ID':<25} | {'SIZE':<5} | {'RISK':<8} | REASON")
    print("-" * 70)
    for item in data:
        rid = item.get("ResourceID") or item.get("VolumeID", "N/A")
        size = item.get("SizeGB", "?")
        risk = item.get("Risk", "N/A")
        reason = item.get("Reason", "")
        if isinstance(size, (int, float)):
            size = str(size)
        print(f"{rid:<25} | {size:<5}GB | {risk:<8} | {reason}")

if __name__ == "__main__":
    display_report()