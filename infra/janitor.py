import boto3
import sys

# Configuration
LOCALSTACK_ENDPOINT = "http://localhost:4566"
AWS_REGION = "us-east-1"

# Initialize Client
ec2 = boto3.client(
    'ec2',
    endpoint_url=LOCALSTACK_ENDPOINT,
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name=AWS_REGION
)

def delete_resource():
    # Validation
    if len(sys.argv) < 2:
        print("ERROR: Missing positional argument [VolumeID].")
        print("Usage: python3 janitor.py <volume-id>")
        return

    target_id = sys.argv[1]

    # Verification Prompt
    confirmation = input(f"CONFIRMATION: Delete resource {target_id}? [y/N]: ")
    
    if confirmation.lower() == 'y':
        try:
            ec2.delete_volume(VolumeId=target_id)
            print(f"SUCCESS: Resource {target_id} has been decommissioned.")
        except Exception as e:
            print(f"FAILURE: Execution failed for {target_id}. {str(e)}")
    else:
        print("ABORT: Operation cancelled by user.")

if __name__ == "__main__":
    delete_resource()