import logging

from cu2 import AWSInstance, SecretAWS, SetupSMTP


def setup_logging():
    logging.basicConfig(filename="smtp_setup.log", level=logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
    )
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)


if __name__ == "__main__":
    setup_logging()
    aws_instance = AWSInstance(
        SecretAWS.aws_access_key,
        SecretAWS.aws_secret_key,
        SecretAWS.instance_id,
        SecretAWS.pem_file_path,
        SecretAWS.region,
    )

    SetupSMTP().run(aws_instance)
