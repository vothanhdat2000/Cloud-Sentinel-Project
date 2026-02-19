"""
Policy-based EBS audit: encryption and tagging compliance.
Writes audit_report.json for viewer/notifier. Use env vars for endpoint/creds.
"""
import json
import logging
import os

import boto3

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ENDPOINT = os.environ.get("LOCALSTACK_ENDPOINT", "http://localhost:4566")
REGION = os.environ.get("AWS_REGION", "us-east-1")
REPORT_PATH = os.environ.get("SENTINEL_REPORT_PATH", "audit_report.json")


def get_ec2_client():
    return boto3.client(
        "ec2",
        endpoint_url=ENDPOINT,
        region_name=REGION,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
    )


def run_audit():
    logger.info("Initiating policy compliance audit...")
    try:
        ec2 = get_ec2_client()
        volumes = ec2.describe_volumes().get("Volumes", [])
        report = []

        for vol in volumes:
            v_id = vol["VolumeId"]
            is_encrypted = vol.get("Encrypted", False)
            tags = {t["Key"]: t["Value"] for t in vol.get("Tags", [])}
            env = tags.get("Env", "Unknown")
            owner = tags.get("Owner", "Missing")

            issue = None
            risk_level = "NONE"

            if env == "Production" and not is_encrypted:
                issue = "CRITICAL: Production volume is not encrypted."
                risk_level = "HIGH"
            elif owner == "Missing":
                issue = "ADVISORY: Orphaned volume (No Owner tag)."
                risk_level = "MEDIUM"

            if issue:
                report.append({
                    "VolumeID": v_id,
                    "ResourceID": v_id,
                    "SizeGB": vol["Size"],
                    "Risk": risk_level,
                    "Reason": issue,
                    "Impact": f"Estimated Cost Leak: ${vol['Size'] * 0.1}/month",
                })
                logger.warning("[%s] %s - %s", risk_level, v_id, issue)

        with open(REPORT_PATH, "w") as f:
            json.dump(report, f, indent=4)
        logger.info("Audit finished. %s issues found.", len(report))
        return len(report)
    except Exception as e:
        logger.exception("Audit failed: %s", e)
        raise


if __name__ == "__main__":
    run_audit()
