"""
Seed non-compliant EBS volumes for DEMO only.
These are NOT in Terraform. In real life they are "drift" (human error, legacy).
Here we create them so Sentinel can find them and Janitor can remove them.
After removal, they stay gone — no Terraform apply will bring them back.
"""
import os
import logging

import boto3

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ENDPOINT = os.environ.get("LOCALSTACK_ENDPOINT", "http://localhost:4566")
REGION = os.environ.get("AWS_REGION", "us-east-1")


def get_ec2():
    return boto3.client(
        "ec2",
        endpoint_url=ENDPOINT,
        region_name=REGION,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
    )


# Same AZ as Terraform so they show up in the same region
AZ = os.environ.get("AWS_AVAILABILITY_ZONE", "us-east-1a")

DEMO_VOLUMES = [
    {"size": 5, "encrypted": False, "tags": [{"Key": "Name", "Value": "test-temporary-disk"}]},
    {
        "size": 50,
        "encrypted": False,
        "tags": [
            {"Key": "Name", "Value": "Finance-Records-2025"},
            {"Key": "Env", "Value": "Production"},
        ],
    },
]


def run():
    ec2 = get_ec2()
    created = []
    for i, spec in enumerate(DEMO_VOLUMES):
        tags = spec.get("tags", [])
        try:
            vol = ec2.create_volume(
                AvailabilityZone=AZ,
                Size=spec["size"],
                Encrypted=spec.get("encrypted", False),
                TagSpecifications=[{"ResourceType": "volume", "Tags": tags}],
            )
            vid = vol["VolumeId"]
            created.append(vid)
            logger.info("Created demo junk volume %s (will be flagged by Sentinel)", vid)
        except Exception as e:
            logger.warning("Could not create volume %s: %s", i + 1, e)
    if created:
        logger.info("Done. Run sentinel.py to audit, then janitor.py <volume-id> to remove.")
    return created


if __name__ == "__main__":
    run()
