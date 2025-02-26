import logging
import smtplib
import time
from email.mime.text import MIMEText

from colorama import Fore


class SendMail:

    def send_mail(self, from_email, password, to_email, subject, body):

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        logging.info(f"{from_email=}")
        logging.info(f"{to_email=}")
        logging.info(f"{subject=}")
        logging.info(f"{body=}")

        try:
            with smtplib.SMTP(
                self.aws_instance.public_ip, self.smtp_port
            ) as server:
                server.set_debuglevel(1)  # Enable debug output
                server.login(from_email, password)  # Authenticate user
                server.sendmail(from_email, [to_email], msg.as_string())
            logging.info(
                f"{Fore.GREEN}Test email sent successfully to {to_email}"
            )
        except smtplib.SMTPAuthenticationError as e:
            logging.error(f"SMTP Authentication Error: {e}")
        except Exception as e:
            logging.error(f"Failed to send test email: {e}")

    def run(self):

        self.send_test_email_external()
        time.sleep(10)
