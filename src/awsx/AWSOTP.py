import logging
import random

import boto3

from cu2 import SecretAWS


class AWSOTP:
    def __init__(self, phone_number):
        self.phone_number = phone_number

    def get_otp(self) -> str:

        otp = str(random.randint(100000, 999999))
        otp = otp[:3] + "-" + otp[3:]
        return otp

    def send(self):

        boto3.setup_default_session(
            aws_access_key_id=SecretAWS.aws_access_key,
            aws_secret_access_key=SecretAWS.aws_secret_key,
            region_name=SecretAWS.region,
        )

        otp = self.get_otp()

        sns_client = boto3.client("sns", region_name=SecretAWS.region)

        response = sns_client.publish(
            PhoneNumber=self.phone_number,
            Message=f"Your OTP is: {otp}",
        )
        message_id = response["MessageId"]

        logging.info(f"OTP sent to {self.phone_number} " + f"({message_id})")

        return otp
