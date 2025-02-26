import logging
import smtplib
import time
from email.mime.text import MIMEText

from colorama import Fore

from cu2 import SecretTestUser


class SendTestEmail:
    def __init__(self, aws_instance):

        self.aws_instance = aws_instance

        self.smtp_port = "22"

        self.test_user = "test@e2ude.com"
        self.test_password = "password123"

    def send_test_email_external(self):
        sender = self.test_user
        recipient = SecretTestUser.email
        subject = f"Test at {time.ctime()}"
        body = "This is a test email sent from the external SMTP client."

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient
        logging.info(msg)
        try:
            with smtplib.SMTP(
                self.aws_instance.public_ip, self.smtp_port
            ) as server:
                server.set_debuglevel(1)  # Enable debug output
                server.login(
                    self.test_user, self.test_password
                )  # Authenticate user
                server.sendmail(sender, [recipient], msg.as_string())
            logging.info(
                f"{Fore.GREEN}Test email sent successfully to {recipient}"
            )
        except smtplib.SMTPAuthenticationError as e:
            logging.info(f"{Fore.RED}SMTP Authentication Error: {e}")
            logging.error(f"SMTP Authentication Error: {e}")
        except Exception as e:
            logging.info(f"{Fore.RED}Failed to send test email: {e}")
            logging.error(f"Failed to send test email: {e}")

    def run(self):

        self.send_test_email_external()
        time.sleep(10)
