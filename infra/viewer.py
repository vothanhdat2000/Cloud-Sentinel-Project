# viewer.py
import json
import os

REPORT_FILE = "audit_report.json"

def display_report():
    if not os.path.exists(REPORT_FILE):
        print("ERROR: No audit report found. Please run sentinel.py first.")
        return

    with open(REPORT_FILE, "r") as f:
        data = json.load(f)

    if not data:
        print("CLEAN: No non-compliant resources found in the report.")
        return

    print(f"{'RESOURCE ID':<25} | {'SIZE':<5} | {'REASON'}")
    print("-" * 60)
    
    for item in data:
        print(f"{item['ResourceID']:<25} | {item['SizeGB']:<5}GB | {item['Reason']}")

if __name__ == "__main__":
    display_report()