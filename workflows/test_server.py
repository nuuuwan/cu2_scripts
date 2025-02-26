import logging
import time

from cu2 import SMTPServer


def setup_logging():
    logging.basicConfig(filename="smtp_setup.log", level=logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)


if __name__ == "__main__":
    print("-" * 64)
    setup_logging()
    server = SMTPServer()
    # server.setup()
    # print("-" * 64)

    username = "nicholas1@" + server.domain
    password = "skin_in_the_game"
    server.add_user(username, password)
    print("-" * 64)

    from_email = username
    to_email = "nuuuwan@gmail.com"
    subject = f"Test Email from {username} set at {time.ctime()}"
    body = subject
    server.send_mail(from_email, password, to_email, subject, body)
    print("-" * 64)
