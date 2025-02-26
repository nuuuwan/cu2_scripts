import colorama

from common import ConfigFile
from cu2 import SecretDomain


class SetupPostfix:
    def __init__(self, aws_instance):

        self.aws_instance = aws_instance

        self.smtp_port = "25"
        self.hostname = "localhost"
        self.domain = SecretDomain.domain
        self.mydestination = "$myhostname, localhost.$mydomain, localhost"

        colorama.init(autoreset=True)

    def install_postfix(self):
        self.aws_instance.execute_commands(["sudo yum install -y postfix"])

    def create_main_cf(self):
        ConfigFile("main.cf").write(
            dict(
                inet_interfaces="all",
                myhostname=self.hostname,
                mydomain=self.domain,
                myorigin="$mydomain",
                mynetworks_style="host",
                home_mailbox="Maildir/",
                smtp_use_tls="no",
                smtp_tls_security_level="may",
                smtp_tls_note_starttls_offer="yes",
                smtpd_banner="$myhostname ESMTP $mail_name ($mail_version)",
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
                smtpd_sasl_auth_enable="yes",
                smtpd_sasl_security_options="noanonymous",
                smtpd_sasl_local_domain="",
                broken_sasl_auth_clients="yes",
                smtpd_sasl_type="dovecot",
                smtpd_sasl_path="private/auth",
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

    def check_postfix_logs(self):
        self.aws_instance.execute_commands(["sudo tail -n 10 /var/log/maillog"])
