# Route53 Domain Updater

This script will update the A record of a Route53 hosted zone with either the IP of from another A record or a specific IP4 address.

A use case (but not limited to this) is updating the A record of an apex domain (e.g. example.com) to point to the public IP of a "DynDns" IP. Since Route53 does not support CNAME records for apex domains, this script will update the A record of the apex domain to point to the IP of another A record. This script is intended to be run as a cron job.

## Usage

Credentials for AWS (with sufficient permissions) and the Hosted Zone ID of the domain to update are required.

### AWS Credentials

To create AWS credentials that are limited to updating Route 53 records, you will need to:

1. Create an IAM Policy with the required permissions.
2. Create an IAM User and attach the policy to that user.
3. Obtain the Access Key ID and Secret Access Key for the IAM User.

#### Step 1: Create an IAM Policy

1. Sign in to the AWS Management Console.
2. Go to IAM (Identity and Access Management) .
3. In the left navigation pane, click on Policies.
4. Click the Create policy button.
5. Switch to the JSON tab and paste the following JSON policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "route53:ChangeResourceRecordSets",
                "route53:ListHostedZones",
                "route53:ListResourceRecordSets"
            ],
            "Resource": [
                "arn:aws:route53:::hostedzone/YOUR_HOSTED_ZONE_ID"
            ]
        }
    ]
}
```

Replace YOUR_HOSTED_ZONE_ID with the actual Hosted Zone ID for your domain.

6. Click Review policy.
7. Give your policy a Name (e.g., Route53UpdatePolicy) and add an optional Description.
8. Click Create policy.

#### Step 2: Create an IAM User

1. In the IAM console, click on Users in the left navigation pane.
2. Click the Add user button.
3. Enter a User name (e.g., Route53Updater).
4. For Access type, select Programmatic access.
5. Click Next: Permissions.
6. Select Attach existing policies directly.
7. Search for the policy you created earlier (e.g., Route53UpdatePolicy) and select it.
8. Click Next: Tags (you can optionally add tags) and then Next: Review.
9. Review the settings and click Create user.

#### Step 3: Obtain Access Key ID and Secret Access Key

1. After creating the user, you should see a success message with the user's Access Key ID and Secret Access Key.
2. Download the .csv file containing these credentials or copy them to a secure location since this is the only time you'll be able to see the secret access key.

### Build the Docker image

```
docker build -t route53-domain-updater .
```

### Run the Docker container

Replace the environment variables with your actual values.

```
docker run --rm \
    -e AWS_ACCESS_KEY_ID=MY_AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=MY_AWS_ACCESS_KEY_ID \
    -e AWS_DEFAULT_REGION=MY_AWS_DEFAULT_REGION \
    -e R53DU_HOSTED_ZONE_ID=MY_HOSTED_ZONE_ID \
    -e R53DU_TARGET_A_RECORD=MY_APEX_DOMAIN \
    -e R53DU_SOURCE_A_RECORD=MY_A_RECORD \
    route53-domain-updater
```
