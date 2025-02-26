import logging

from passlib.hash import sha512_crypt


class SetupDovecot:

    def install_dovecot(self):

        self.aws_instance.execute_commands(
            [
                "sudo yum install -y dovecot",
            ]
        )

    def create_dovecot_conf(self):

        dovecot_conf_content = """
        protocols = imap pop3 lmtp
        mail_location = maildir:~/Maildir
        passdb {
          driver = passwd-file
          args = /etc/dovecot/passwd
        }
        userdb {
          driver = passwd
        }
        auth_mechanisms = plain login
        service auth {
          unix_listener /var/spool/postfix/private/auth {
            mode = 0660
            user = postfix
            group = postfix
          }
          unix_listener auth-userdb {
            mode = 0600
            user = dovecot
            group = dovecot
          }
          user = root
        }
        """

        with open("dovecot.conf", "w") as file:
            file.write(dovecot_conf_content)

    def create_passwd_file(self):

        with open("passwd", "w") as file:
            file.write("")

    def copy_dovecot_files_to_instance(self):
        self.aws_instance.upload_file(
            "dovecot.conf", "/home/ec2-user/dovecot.conf"
        )
        self.aws_instance.upload_file("passwd", "/home/ec2-user/passwd")
        self.aws_instance.execute_commands(
            [
                "sudo mv /home/ec2-user/dovecot.conf /etc/dovecot/dovecot.conf",
                "sudo mv /home/ec2-user/passwd /etc/dovecot/passwd",
                "sudo chown root:root /etc/dovecot/dovecot.conf /etc/dovecot/passwd",
                "sudo chmod 640 /etc/dovecot/passwd",
                "sudo chmod 644 /etc/dovecot/dovecot.conf",
                "sudo chown -R dovecot:dovecot /var/run/dovecot",
                "sudo cat /etc/dovecot/passwd",
            ]
        )

    def configure_sasl_auth(self):
        sasl_auth_content = """
        auth_mechanisms = plain login
        service auth {
          unix_listener /var/spool/postfix/private/auth {
            mode = 0660
            user = postfix
            group = postfix
          }
        }
        """

        with open("sasl_auth.conf", "w") as file:
            file.write(sasl_auth_content)

    def copy_sasl_auth_to_instance(self):
        self.aws_instance.upload_file(
            "sasl_auth.conf", "/home/ec2-user/sasl_auth.conf"
        )
        self.aws_instance.execute_commands(
            [
                "sudo mv /home/ec2-user/sasl_auth.conf /etc/dovecot/conf.d/10-auth.conf",
                "sudo chown root:root /etc/dovecot/conf.d/10-auth.conf",
                "sudo chmod 644 /etc/dovecot/conf.d/10-auth.conf",
            ]
        )

    def start_dovecot(self):
        self.aws_instance.execute_commands(
            [
                "sudo mkdir -p /var/run/dovecot",
                "sudo chown dovecot:dovecot /var/run/dovecot",
                "sudo systemctl stop dovecot",
                "sudo systemctl start dovecot",
                "sudo systemctl enable dovecot",
                "sudo systemctl status dovecot",
            ]
        )

    def add_user(self, username, password):

        hashed_password = sha512_crypt.hash(password)
        new_user_entry = f"{username}:{hashed_password}\n"
        logging.info(f"Adding user to passwd file: {new_user_entry}")

        with open("passwd", "a") as file:
            file.write(new_user_entry)

        self.aws_instance.upload_file("passwd", "/home/ec2-user/passwd")
        self.aws_instance.execute_commands(
            [
                "sudo mv /home/ec2-user/passwd /etc/dovecot/passwd",
                "sudo chown root:root /etc/dovecot/passwd",
                "sudo chmod 640 /etc/dovecot/passwd",
                "sudo systemctl reload dovecot",
            ]
        )
