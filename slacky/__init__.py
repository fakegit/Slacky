from slacky.config import load_config as lc
from slacky.api.auth import authenticate
from colorama import init
from colorama import Fore, Back, Style
from time import time
from argparse import ArgumentParser
import httpx, json, logging, getpass
import nest_asyncio

nest_asyncio.apply()

class Prefixes:
    info = str('[' + Fore.GREEN + Style.BRIGHT + 'INFO' + Style.RESET_ALL + '] ')
    warning = str('[' + Fore.YELLOW + Style.BRIGHT + 'WARNING' + Style.RESET_ALL + '] ')
    event = str('[' + Fore.BLUE + Style.BRIGHT + 'EVENT' + Style.RESET_ALL + '] ')
    error = str('[' + Fore.RED + Style.BRIGHT + 'ERROR' + Style.RESET_ALL + '] ')
    start = str('[' + Fore.LIGHTBLUE_EX + Style.BRIGHT + 'SLACKY' + Style.RESET_ALL + '] ')

class CustomReplies:
    def __init__(self, config):
        self.custom_replies = config['custom_replies']
        self.last_sent = False

    def add(self, custom_reply):
        self.custom_replies.append(custom_reply)
        with open('config.json', 'r+') as file:
            obj = json.load(file)
            obj['custom_replies'] = self.custom_replies
            file.seek(0)
            json.dump(obj, file, indent=4)
            file.truncate()
    
    def delete(self, num):
        del self.custom_replies[int(num)]
        with open('config.json', 'r+') as file:
            obj = json.load(file)
            obj['custom_replies'] = self.custom_replies
            file.seek(0)
            json.dump(obj, file, indent=4)
            file.truncate()

class Listeners:
    def __init__(self, config):
        self.listeners = config['listeners']

    def add(self, phrase):
        self.listeners.append(phrase)
        with open('config.json', 'r+') as file:
            obj = json.load(file)
            obj['listeners'] = self.listeners
            file.seek(0)
            json.dump(obj, file, indent=4)
            file.truncate()
    
    def delete(self, phrase):
        num = self.listeners.index(phrase)
        del self.listeners[num]
        with open('config.json', 'r+') as file:
            obj = json.load(file)
            obj['listeners'] = self.listeners
            file.seek(0)
            json.dump(obj, file, indent=4)
            file.truncate()

def check_user(user):
    if user == config['user']:
        return True
    else:
        return False

def config_parser():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', help='Optional path to load different config or create new')
    return parser

try:
    parser = config_parser()
    args = parser.parse_args()
    if args.config:
        print('THere was')
        config_path = args.config
    else:
        config_path = './config.json'
    print(Prefixes.start + 'Welcome to Slacky v1.1.1 | The First Python Self-Bot for Slack!')
    print(Prefixes.event + 'Searching for New Updates...')
    with open('version.txt', 'r') as file:
        version = str(file.read())

    remote_v = httpx.get('https://raw.githubusercontent.com/M4cs/Slacky/master/version.txt')
    rv = remote_v.content.decode('utf-8')

    if version != rv:
        print(Prefixes.warning + 'Newer Version Available! Please re-pull to update.')
    else:
        print(Prefixes.info + 'Up to Date!')
    config = lc(config_path)
    if not config:
        print(Prefixes.warning + 'No Config File Found. Starting Wizard.')
        print(Prefixes.start + 'Enter Legacy Workspace Token (Starts w/ xoxp)')
        token = input('> ')
        print(Prefixes.start + 'Enter User ID. Google How To Get This.')
        user_id = input('> ')
        print(Prefixes.start + 'Enter Desired Prefix (Default: ~)')
        prefix = input('> ')
        if prefix == '' or prefix == None:
            prefix = '~'
        else:
            prefix = prefix
        print(Prefixes.info + 'Entered Token:', token)
        print(Prefixes.info + 'Entered User ID:', user_id)
        print(Prefixes.info + 'Entered Prefix:', prefix)
        print(Prefixes.start + 'Press ENTER to Confirm Information or Ctrl+C to Quit.')
        getpass.getpass('')
        with open('config.json', 'w+') as file:
            config = {
                'token': token,
                'user': user_id,
                'prefix': prefix,
                'listeners': [],
                'custom_replies': []
            }
            json.dump(config, file, indent=4)
        print(Prefixes.event + 'Config Saved! Please Restart To Use Slacky')
        exit(0)

    print(Prefixes.info + 'Config Loaded')
    print(Prefixes.event + 'Attempting to Authenticate with Slack', end='\r')
    listener = Listeners(config)
    customrs = CustomReplies(config)
    client = authenticate(config)
    if not client:
        print(Prefixes.error + 'Could Not Authenticate with Slack! Please check your config and token!')
    print(' ' * 65, end='\r')
    user = client.users_info(user=config['user'])
    team = client.team_info()['team']['domain']
    print(Prefixes.info + 'Logged in as {}@{}'.format(user['user']['name'], team))
except KeyboardInterrupt:
    print(Prefixes.event + 'Shutdown Called')
    exit(0)