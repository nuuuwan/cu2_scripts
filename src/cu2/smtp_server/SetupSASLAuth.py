


class SetupSASLAuth:

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
