import os
import boto3
import requests
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import argparse

def get_ip_address(domain):
    response = requests.get(f'https://dns.google/resolve?name={domain}&type=A')
    response.raise_for_status()
    data = response.json()
    ip_address = data['Answer'][0]['data']
    return ip_address



def update_route53_record(ip_address, hosted_zone_id, domain_name):
    client = boto3.client(
        'route53',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),        # AWS_ACCESS_KEY_ID 
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY') # AWS_SECRET_ACCESS_KEY
    )

    try:
        response = client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain_name,
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [{'Value': ip_address}]
                    }
                }]
            }
        )
        print(response)
    except NoCredentialsError:
        print("No credentials provided or found.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
    except Exception as e:
        print(f"Error updating Route 53 record: {e}")

def main():
    parser = argparse.ArgumentParser(description='Route53 Domain Updater.')

    # Add arguments/flags
    parser.add_argument('-ta', '--target-a-record', type=str, help='Target A record to update')
    parser.add_argument('-hz', '--hosted-zone-id', type=str, help='The hosted ZONE ID if the target A record as defined in Route53')
    parser.add_argument('-sa', '--source-a-record', type=str, help='Domain Name (must be A record) to update the target A record with')
    parser.add_argument('-ip4', '--source-ip4-address', type=str, help='IP4 address to update the target A record with')

    # Parse the arguments
    args = parser.parse_args()

    target_a_record = args.target_a_record
    hosted_zone_id = args.hosted_zone_id
    source_a_record = args.source_a_record
    source_ip4_address = args.source_ip4_address

    if not hosted_zone_id:
        hosted_zone_id = os.getenv('R53DU_HOSTED_ZONE_ID')
    if not hosted_zone_id:
        hosted_zone_id = os.getenv('HOSTED_ZONE_ID')

    if not target_a_record:
        target_a_record = os.getenv('R53DU_TARGET_A_RECORD')
    if not target_a_record:
        target_a_record = os.getenv('APEX_DOMAIN')

    if not source_a_record:
        source_a_record = os.getenv('R53DU_SOURCE_A_RECORD')
    if not source_a_record:
        source_a_record = os.getenv('A_RECORD')

    if not source_ip4_address:
        source_ip4_address = os.getenv('R53DU_SOURCE_IP4_ADDRESS')

    print(f'Target domain: {target_a_record}')
    print(f'Hosted Zone ID: {hosted_zone_id}')
    print(f'Source A record: {source_a_record}')
    print(f'Source IP4 address: {source_ip4_address}')

    if not hosted_zone_id:
        parser.error('At least one of --hosted-zone-id or env.R53DU_HOSTED_ZONE_ID or env.HOSTED_ZONE_ID must be specified.')

    if not target_a_record:
        parser.error('At least one of --target_a_record or env.R53DU_TARGET_A_RECORD or env.APEX_DOMAIN must be specified.')

    if not source_a_record and not source_ip4_address:
        parser.error('At least one of --source-a-record or env.R53DU_SOURCE_A_RECORD or env.A_RECORD or or --source-ip4-address or env.R53DU_SOURCE_IP4_ADDRESS must be specified.')

    try:
        ip_address = source_ip4_address
        if not ip_address:
            ip_address = get_ip_address(source_a_record)
            print(f'Current IP address of {source_a_record}: {ip_address}')
        
        update_route53_record(ip_address, hosted_zone_id, target_a_record)
        print(f'Successfully updated Route 53 A record for {target_a_record} to {ip_address}')
    except requests.RequestException as e:
        print(f"Error fetching IP address: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
