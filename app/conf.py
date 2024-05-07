import os
from dotenv import dotenv_values

# Load environment variables from .env file
class Secret:

    def __init__(self):
        # get full path of a file name .env
        path = os.path.join(os.path.dirname(__file__), './../.env')
        env_vals = dotenv_values(path)
        self.SECRETS = dict(env_vals)

    def __getitem__(self, secret):
        return self.SECRETS[secret]