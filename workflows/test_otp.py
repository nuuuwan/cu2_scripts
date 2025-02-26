import random

import boto3

from cu2 import SecretAWS, SecretTestUser

# Set up AWS credentials
boto3.setup_default_session(
    aws_access_key_id=SecretAWS.aws_access_key,
    aws_secret_access_key=SecretAWS.aws_secret_key,
    region_name=SecretAWS.region,
)

# Generate a 6-digit OTP
otp = str(random.randint(100000, 999999))
otp = otp[:3] + "-" + otp[3:]
print(f"{otp=}")

# Initialize SNS client
sns_client = boto3.client("sns", region_name=SecretAWS.region)

phone_number = SecretTestUser.phone_num
print(f"{phone_number=}")

# Send OTP via SMS
response = sns_client.publish(
    PhoneNumber=phone_number,
    Message=f"Your OTP is: {otp}",
)

# Print response
print("Message Sent! Message ID:", response["MessageId"])
