import logging

from cu2 import SMTPServer


def setup_logging():
    logging.basicConfig(filename="smtp_setup.log", level=logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)


if __name__ == "__main__":
    setup_logging()
    SMTPServer().run()
