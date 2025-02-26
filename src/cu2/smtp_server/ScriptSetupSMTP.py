import time

import colorama
from colorama import Fore, Style

from awsx import AWSInstance
from cu2 import SecretAWS, SecretDomain, SecretTestUser


class ScriptSetupSMTP:
    def __init__(self):

        self.aws_instance = AWSInstance(
            SecretAWS.aws_access_key,
            SecretAWS.aws_secret_key,
            SecretAWS.instance_id,
            SecretAWS.pem_file_path,
            SecretAWS.region,
        )

        self.smtp_port = "25"
        self.hostname = "localhost"
        self.domain = SecretDomain.domain
        self.mydestination = "$myhostname, localhost.$mydomain, localhost"

        colorama.init(autoreset=True)

    def update_system(self):
        # Update the system packages and install necessary software
        commands = [
            "sudo yum update -y",
            "sudo yum install -y postfix",
            "sudo yum install -y sendmail sendmail-cf",
        ]
        self.aws_instance.execute_commands(commands)

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

        self.aws_instance.upload_file("main.cf", "/home/ec2-user/main.cf")

        # Move the file to the correct location using sudo
        self.aws_instance.execute_commands(
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
        self.aws_instance.execute_commands(commands)

    def check_postfix_logs(self):
        # Check the Postfix logs for any errors
        commands = ["sudo tail -n 10 /var/log/maillog"]
        self.aws_instance.execute_commands(commands)

    def send_test_email(self):
        print(f"{Fore.GREEN}{Style.BRIGHT}[send_test_email]")
        # Send a test email to verify the SMTP server is working
        sender = "test@" + self.domain
        recipient = SecretTestUser.email
        subject = "Test Email"
        body = (
            f"This is a test email from the SMTP server, sent at {time.ctime()}"
        )

        email_content = (
            f"Subject: {subject}\nFrom: {sender}\nTo: {recipient}\n\n{body}"
        )
        email_file = "test_email.txt"

        with open(email_file, "w") as file:
            file.write(email_content)

        self.aws_instance.upload_file(
            email_file, "/home/ec2-user/test_email.txt"
        )

        try:
            self.aws_instance.execute_commands(
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
        self.setup_smtp_server()


if __name__ == "__main__":
    ScriptSetupSMTP().run()
