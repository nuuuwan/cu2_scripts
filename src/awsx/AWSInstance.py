import boto3  # AWS SDK for Python to interact with AWS services
import paramiko  # Library for making SSH connections to remote machines
from colorama import Fore, Style


class AWSInstance:
    def __init__(
        self,
        aws_access_key,
        aws_secret_key,
        instance_id,
        pem_file_path,
        region,
    ):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.instance_id = instance_id
        self.pem_file_path = pem_file_path
        self.region = region
        self.public_ip = None
        self.ssh = None

        self.connect()

    def __del__(self):
        if self.ssh:
            self.ssh.close()
            print("✅ SSH connection closed.")

    def connect(self):
        print("Connecting to the AWS instance...")
        ec2 = boto3.client(
            "ec2",
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.region,
        )

        reservations = ec2.describe_instances(
            InstanceIds=[self.instance_id]
        ).get("Reservations")
        instance = reservations[0]["Instances"][0]
        self.public_ip = instance["PublicIpAddress"]  # Store public IP
        print(f"✅ Connected to AWS instance on {self.public_ip}.")

        key = paramiko.RSAKey.from_private_key_file(self.pem_file_path)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.public_ip, username="ec2-user", pkey=key)
        print("✅ SSH connection established.")

    def clean(self, s):
        lines = s.split("\n")
        lines = [line.strip() for line in lines]
        return "\n".join([line for line in lines if line])

    def execute_command(self, command):
        print(f"> {Fore.GREEN}{Style.BRIGHT}{command}")
        ___, stdout, stderr = self.ssh.exec_command(command)
        str_out = self.clean(stdout.read().decode())
        if str_out:
            print(f"{Fore.BLUE}{str_out}")
        str_err = self.clean(stderr.read().decode())
        if str_err:
            print(f"{Fore.RED}{str_err}")
        print("...")

    def execute_commands(self, commands):
        for command in commands:
            self.execute_command(command)

    def upload_file(self, local_path, remote_path):
        sftp = self.ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        print(f"✅ Uploaded {local_path} to {remote_path}.")
