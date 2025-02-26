import logging

from passlib.hash import sha512_crypt

from awsx import AWSOTP
from cu2.smtp_server import SMTPServer


class EmailClient:

    def normalize_phone_num(self, phone_num):
        phone_num = phone_num.replace(" ", "")
        phone_num = phone_num.replace("-", "")
        phone_num = phone_num.replace("_", "")
        assert len(phone_num) == 10
        return "+94" + phone_num[1:]

    def input_phone_num(self):
        raw_phone_num = input("Enter your phone number: ")
        normalized_phone_num = self.normalize_phone_num(raw_phone_num)
        logging.info("Normalized phone number: " + normalized_phone_num)
        return normalized_phone_num

    def input_otp(self):
        return input("Enter the OTP: ")

    def login(self, phone_num, otp):
        logging.info("Logging in...")

    def input_message(self):
        return input("Enter the message: ")

    def input_to_email(self):
        return input("Enter the recipient's email: ")

    def send_message(self, email, message):
        logging.info(f'Sending message "{message}" from {email}...')

    def logout(self):
        logging.info("Logging out...")

    def run(self):
        phone_num = self.input_phone_num()
        from_email = f"{phone_num}@mail.org"
        expected_otp = AWSOTP(phone_num).send()
        observed_otp = self.input_otp()

        if observed_otp != expected_otp:
            logging.error("Invalid OTP")
            return

        subject = self.input_message()
        body = subject

        print("-" * 64)

        server = SMTPServer()

        password = sha512_crypt.hash(from_email + expected_otp)
        server.add_user(from_email, from_email + expected_otp)
        print("-" * 64)

        to_email = self.input_to_email()

        server.send_mail(from_email, password, to_email, subject, body)
        print("-" * 64)
