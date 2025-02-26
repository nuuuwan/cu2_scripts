from cu2 import EmailClient
from workflows.test_server import setup_logging

if __name__ == "__main__":
    setup_logging()
    EmailClient().run()
