import boto3
import json

# Initialize Client with dummy credentials for LocalStack
ec2 = boto3.client(
    'ec2', 
    endpoint_url='http://localhost:4566', 
    region_name='us-east-1',
    aws_access_key_id='test',          # <--- Add this
    aws_secret_access_key='test'       # <--- Add this
)

def run_audit():
    print("LOG: Initiating Corporate Policy Compliance Audit...")
    try:
        volumes = ec2.describe_volumes().get('Volumes', [])
        report = []

        for vol in volumes:
            v_id = vol['VolumeId']
            is_encrypted = vol.get('Encrypted', False)
            tags = {t['Key']: t['Value'] for t in vol.get('Tags', [])}
            env = tags.get('Env', 'Unknown')
            owner = tags.get('Owner', 'Missing')

            issue = None
            risk_level = "NONE"

            # POLICY 1: Production volumes MUST be encrypted
            if env == "Production" and not is_encrypted:
                issue = "CRITICAL: Production volume is not encrypted."
                risk_level = "HIGH"
            
            # POLICY 2: All volumes must have an Owner for accountability
            elif owner == "Missing":
                issue = "ADVISORY: Orphaned volume (No Owner tag)."
                risk_level = "MEDIUM"

            if issue:
                report.append({
                    "VolumeID": v_id,
                    "Risk": risk_level,
                    "Reason": issue,
                    "Impact": f"Estimated Cost Leak: ${vol['Size'] * 0.1}/month"
                })
                print(f"ALERT [{risk_level}]: {v_id} - {issue}")

        with open("audit_report.json", "w") as f:
            json.dump(report, f, indent=4)
        print(f"SUMMARY: Audit finished. {len(report)} issues found.")
        
    except Exception as e:
        print(f"ERROR: Audit failed. {str(e)}")

if __name__ == "__main__":
    run_audit()