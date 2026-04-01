from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path('.env'))
from instagrapi import Client
import os

cl = Client()
cl.challenge_code_handler = lambda u, c: input('2FA code: ')
cl.login(os.environ['IG_USERNAME'], os.environ['IG_PASSWORD'])
cl.dump_settings('.tmp/ig_session_neo.json')
print('Neo done — session saved')
