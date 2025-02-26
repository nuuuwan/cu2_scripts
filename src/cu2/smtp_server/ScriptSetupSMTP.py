import smtplib
import time
from email.mime.text import MIMEText

import colorama
from colorama import Fore

from awsx import AWSInstance
from common import ConfigFile
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
            "sudo yum install -y telnet",
        ]
        self.aws_instance.execute_commands(commands)

    def create_main_cf(self):
        ConfigFile("main.cf").write(
            dict(
                inet_interfaces="all",
                myhostname=self.hostname,
                mydomain=self.domain,
                myorigin="$mydomain",
                mynetworks_style="host",
                home_mailbox="Maildir/",
                smtp_use_tls="yes",
                smtp_tls_security_level="may",
                smtp_tls_note_starttls_offer="yes",
                smtpd_banner="$myhostname ESMTP $mail_name ($mail_version)",
                smtpd_tls_cert_file="",
                smtpd_tls_key_file="",
                smtpd_tls_CAfile="",
                smtpd_tls_security_level="may",
                smtpd_tls_auth_only="no",
                smtpd_tls_received_header="yes",
                smtpd_tls_session_cache_timeout="3600s",
                tls_random_source="dev:/dev/urandom",
                maillog_file="/var/log/maillog",
                smtpd_recipient_restrictions=",".join(
                    [
                        "permit_mynetworks",
                        "permit_sasl_authenticated",
                        "reject_unauth_destination",
                    ]
                ),
                relay_domains="proton.me",
                relay_recipient_maps="hash:/etc/postfix/relay_recipients",
            )
        )

    def copy_main_cf_to_instance(self):
        self.aws_instance.upload_file("main.cf", "/home/ec2-user/main.cf")
        self.aws_instance.execute_commands(
            ["sudo mv /home/ec2-user/main.cf /etc/postfix/main.cf"]
        )

    def start_postfix(self):
        self.aws_instance.execute_commands(
            [
                "sudo systemctl stop postfix",
                "sudo systemctl start postfix",
                "sudo systemctl enable postfix",
                "sudo systemctl status postfix",
            ]
        )

    def check_domains(self):
        self.aws_instance.execute_commands(
            [
                "nslookup proton.me",
                "nslookup -type=MX proton.me",
            ]
        )

    def check_postfix_logs(self):
        self.aws_instance.execute_commands(["sudo tail -n 10 /var/log/maillog"])

    def build_email_content(self):
        sender = "test111@" + "gmail.com"
        recipient = SecretTestUser.email
        subject = f"Test at {time.ctime()}"
        body = subject
        email_content = (
            f"Subject: {subject}\nFrom: {sender}\nTo: {recipient}\n\n{body}"
        )
        email_file = "test_email.txt"
        with open(email_file, "w") as file:
            file.write(email_content)
        return email_file, sender, recipient

    def send_test_email_internal(self):
        email_file, sender, recipient = self.build_email_content()
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

    def send_test_email_external(self):
        sender = "test@" + self.domain
        recipient = SecretTestUser.email
        subject = f"Test at {time.ctime()}"
        body = "This is a test email sent from the external SMTP client."

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        try:
            with smtplib.SMTP(
                self.aws_instance.public_ip, self.smtp_port
            ) as server:
                server.set_debuglevel(1)  # Enable debug output
                server.sendmail(sender, [recipient], msg.as_string())
            print(f"{Fore.GREEN}Test email sent successfully to {recipient}")
        except Exception as e:
            print(f"{Fore.RED}Failed to send test email: {e}")

    def run(self):
        self.update_system()
        self.create_main_cf()
        self.copy_main_cf_to_instance()
        self.start_postfix()
        self.check_domains()
        self.check_postfix_logs()
        self.send_test_email_external()
        time.sleep(10)
        self.check_postfix_logs()


if __name__ == "__main__":
    ScriptSetupSMTP().run()
