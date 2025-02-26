from awsx import AWSInstance
from cu2.secrets import SecretAWS, SecretDomain
from cu2.smtp_server.SendMail import SendMail
from cu2.smtp_server.SetupDovecot import SetupDovecot
from cu2.smtp_server.SetupPostfix import SetupPostfix
from cu2.smtp_server.SetupSASLAuth import SetupSASLAuth


class SMTPServer(SetupDovecot, SetupPostfix, SendMail, SetupSASLAuth):
    def __init__(self):
        self.aws_instance = None

        self.smtp_port = "25"
        self.domain = SecretDomain.domain

        self.aws_setup()

    def aws_setup(self):
        self.aws_instance = AWSInstance(
            SecretAWS.aws_access_key,
            SecretAWS.aws_secret_key,
            SecretAWS.instance_id,
            SecretAWS.pem_file_path,
            SecretAWS.region,
        )

    def setup(self):

        self.install_postfix()
        self.install_dovecot()

        self.create_main_cf()
        self.copy_main_cf_to_instance()

        self.create_dovecot_conf()
        self.create_passwd_file()
        self.copy_dovecot_files_to_instance()

        self.configure_sasl_auth()
        self.copy_sasl_auth_to_instance()

        self.start_postfix()
        self.start_dovecot()

        self.check_postfix_logs()
