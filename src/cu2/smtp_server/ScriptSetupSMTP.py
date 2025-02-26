# Python script that setups an SMTP server on an AWS instance
import os
import time

import boto3  # AWS SDK for Python to interact with AWS services
import colorama
import paramiko  # Library for making SSH connections to remote machines
from colorama import Fore, Style

from cu2 import SecretAWS, SecretDomain, SecretTestUser


class ScriptSetupSMTP:
    def __init__(self):
        self.aws_access_key = None
        self.aws_secret_key = None
        self.instance_id = None
        self.pem_file_path = None
        self.smtp_port = None
        self.hostname = None
        self.domain = None
        self.mydestination = None
        self.ssh = None
        self.region = None  # Add region attribute
        self.public_ip = None  # Add public_ip attribute
        colorama.init(autoreset=True)

    def get_user_inputs(self):
        # Get necessary inputs from the user
        self.aws_access_key = SecretAWS.aws_access_key
        self.aws_secret_key = SecretAWS.aws_secret_key
        self.instance_id = SecretAWS.instance_id
        self.pem_file_path = SecretAWS.pem_file_path
        self.region = SecretAWS.region

        self.smtp_port = "25"
        self.hostname = "localhost"
        self.domain = SecretDomain.domain
        self.mydestination = "$myhostname, localhost.$mydomain, localhost"

    def connect_to_instance(self):
        # Connect to the AWS EC2 instance using provided credentials and PEM
        # file
        ec2 = boto3.client(
            "ec2",
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.region,  # Specify the region
        )
        reservations = ec2.describe_instances(
            InstanceIds=[self.instance_id]
        ).get("Reservations")
        instance = reservations[0]["Instances"][0]
        self.public_ip = instance["PublicIpAddress"]  # Store public IP

        key = paramiko.RSAKey.from_private_key_file(self.pem_file_path)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.public_ip, username="ec2-user", pkey=key)

    def update_system(self):
        # Update the system packages and install necessary software
        commands = [
            "sudo yum update -y",
            "sudo yum install -y postfix",
            "sudo yum install -y sendmail sendmail-cf",
        ]
        self.execute_commands(commands)

    def create_main_cf(self):
        # Create a new main.cf file with the necessary configurations
        main_cf_content = f"""
inet_interfaces = all
myhostname = {self.hostname}
mydomain = {self.domain}
myorigin = $mydomain
mynetworks_style = host
home_mailbox = Maildir/

smtp_use_tls = yes
smtp_tls_security_level = may
smtp_tls_note_starttls_offer = yes

smtpd_banner = $myhostname ESMTP $mail_name ($mail_version)
smtpd_tls_cert_file =
smtpd_tls_key_file =
smtpd_tls_CAfile =
smtpd_tls_security_level = may
smtpd_tls_auth_only = no
smtpd_tls_received_header = yes
smtpd_tls_session_cache_timeout = 3600s
tls_random_source = dev:/dev/urandom

maillog_file = /var/log/maillog

smtpd_recipient_restrictions = permit_mynetworks, permit_sasl_authenticated, reject_unauth_destination
        """
        with open("main.cf", "w") as file:
            file.write(main_cf_content)

    def copy_main_cf_to_instance(self):
        # Copy the main.cf file to the remote instance
        sftp = self.ssh.open_sftp()
        sftp.put("main.cf", "/home/ec2-user/main.cf")
        sftp.close()
        os.remove("main.cf")
        # Move the file to the correct location using sudo
        self.execute_commands(
            ["sudo mv /home/ec2-user/main.cf /etc/postfix/main.cf"]
        )

    def start_postfix(self):
        # Start and enable Postfix service
        commands = [
            "sudo systemctl stop postfix",
            "sudo systemctl start postfix",
            "sudo systemctl enable postfix",
            "sudo systemctl status postfix",
        ]
        self.execute_commands(commands)

    def check_postfix_logs(self):
        # Check the Postfix logs for any errors
        commands = ["sudo tail -n 10 /var/log/maillog"]
        self.execute_commands(commands)

    def clean(self, s):
        lines = s.split("\n")
        lines = [line.strip() for line in lines]
        return "\n".join([line for line in lines if line])

    def execute_commands(self, commands):
        # Execute a list of commands on the remote instance
        for command in commands:
            print(f"> {Fore.GREEN}{Style.BRIGHT}{command}")
            ___, stdout, stderr = self.ssh.exec_command(command)
            str_out = self.clean(stdout.read().decode())
            if str_out:
                print(f"{Fore.BLUE}{str_out}")
            str_err = self.clean(stderr.read().decode())
            if str_err:
                print(f"{Fore.RED}{str_err}")
            print("...")

    def send_test_email(self):
        print(f"{Fore.GREEN}{Style.BRIGHT}[send_test_email]")
        # Send a test email to verify the SMTP server is working
        sender = "test@" + self.domain
        recipient = SecretTestUser.email
        subject = "Test Email"
        body = "This is a test email from the SMTP server."

        email_content = (
            f"Subject: {subject}\nFrom: {sender}\nTo: {recipient}\n\n{body}"
        )
        email_file = "test_email.txt"

        with open(email_file, "w") as file:
            file.write(email_content)

        sftp = self.ssh.open_sftp()
        sftp.put(email_file, "/home/ec2-user/test_email.txt")
        sftp.close()
        os.remove(email_file)

        try:
            self.execute_commands(
                [
                    f"sudo sendmail -f {sender} {recipient} < /home/ec2-user/test_email.txt",
                    "rm /home/ec2-user/test_email.txt",
                ]
            )
            print(f"{Fore.GREEN}Test email sent successfully to {recipient}")
        except Exception as e:
            print(f"{Fore.RED}Failed to send test email: {e}")

    def setup_smtp_server(self):
        self.update_system()
        self.create_main_cf()
        self.copy_main_cf_to_instance()
        self.start_postfix()
        self.check_postfix_logs()
        self.send_test_email()
        time.sleep(10)
        self.check_postfix_logs()

    def run(self):
        # Main function to get inputs, connect to instance,
        # and setup SMTP server
        self.get_user_inputs()
        self.connect_to_instance()
        self.setup_smtp_server()
        self.ssh.close()


if __name__ == "__main__":
    ScriptSetupSMTP().run()
