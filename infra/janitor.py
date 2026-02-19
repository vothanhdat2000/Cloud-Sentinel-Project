"""
Safe EBS volume deletion with confirmation. Uses env for endpoint/creds.
"""
import logging
import os
import sys

import boto3

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ENDPOINT = os.environ.get("LOCALSTACK_ENDPOINT", "http://localhost:4566")
REGION = os.environ.get("AWS_REGION", "us-east-1")


def get_ec2_client():
    return boto3.client(
        "ec2",
        endpoint_url=ENDPOINT,
        region_name=REGION,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
    )


def delete_resource():
    if len(sys.argv) < 2:
        logger.error("Missing VolumeID. Usage: python janitor.py <volume-id>")
        sys.exit(1)

    target_id = sys.argv[1]
    confirmation = input(f"CONFIRM: Delete volume {target_id}? [y/N]: ")

    if confirmation.lower() != "y":
        logger.info("Operation cancelled.")
        return

    try:
        get_ec2_client().delete_volume(VolumeId=target_id)
        logger.info("Resource %s decommissioned.", target_id)
    except Exception as e:
        logger.exception("Failed for %s: %s", target_id, e)
        sys.exit(1)


if __name__ == "__main__":
    delete_resource()
