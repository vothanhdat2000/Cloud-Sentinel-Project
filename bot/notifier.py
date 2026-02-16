# bot/notifier.py
import json
import os

# Path to the shared audit report
REPORT_PATH = "../infra/audit_report.json"

def send_notification():
    if not os.path.exists(REPORT_PATH):
        print("[LOG] Status: No audit report found.")
        return

    try:
        with open(REPORT_PATH, "r") as f:
            report_data = json.load(f)
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse audit_report.json.")
        return

    if not report_data:
        print("[LOG] Status: Infrastructure is compliant. No issues detected.")
        return

    # Visual Header
    print("\n" + "="*70)
    print("           CLOUD SENTINEL - INFRASTRUCTURE COMPLIANCE REPORT          ")
    print("="*70)
    print(f"{'RESOURCE ID':<25} | {'RISK':<8} | {'IMPACT':<15}")
    print("-" * 70)
    
    # Data Rows
    for item in report_data:
        res_id = item['VolumeID']
        risk = item['Risk']
        impact = item['Impact'].split(':')[-1].strip() # Clean up the string
        
        print(f"{res_id:<25} | {risk:<8} | {impact:<15}")
        print(f"REASON: {item['Reason']}")
        print("-" * 70)
    
    # Summary Footer
    print(f"SUMMARY: {len(report_data)} non-compliant resource(s) identified.")
    print("ACTION REQUIRED: Please execute janitor.py for remediation.")
    print("="*70 + "\n")

if __name__ == "__main__":
    send_notification()