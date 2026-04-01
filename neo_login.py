#!/opt/homebrew/bin/python3.11
import sys
sys.path.insert(0, '/Users/tylarkin/Desktop/AI Cnntent Creator workflow')
from dotenv import load_dotenv
load_dotenv('/Users/tylarkin/Desktop/AI Cnntent Creator workflow/.env')
from execution.instagram_client import get_client
print('Logging into Neo...')
cl = get_client(account='neo')
print('Done — session saved!')
