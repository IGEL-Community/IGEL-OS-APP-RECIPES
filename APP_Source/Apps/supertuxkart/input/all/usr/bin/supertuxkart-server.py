#!/usr/bin/env python3

from os import EX_OK, EX_USAGE
import getsetup3
import subprocess

def get_config() -> dict:

    config = {}
    with getsetup3.Getsetup() as gs:
        config = {
            'lan-server': gs.getvalue('app.supertuxkart.server.lan-server'),
            'lan-server-name': gs.getvalue('app.supertuxkart.server.lan-server-name'),
            'server-password': gs.getcryptvalue('app.supertuxkart.server.server-password'),
            'team-choosing': gs.getvalue('app.supertuxkart.server.team-choosing'),
            'battle-mode': gs.getvalue('app.supertuxkart.server.battle-mode')
        }
    return config


config = get_config()

if config['lan-server'] == 'false':
    raise SystemExit(EX_OK)

command=['/services/supertuxkart/usr/games/supertuxkart']

if not config['lan-server-name']:
    print('Error: lan-server-name not set')
    raise SystemExit(EX_USAGE)

command.append(f'--lan-server={config["lan-server-name"]}')

if config['server-password']:
    command.append(f'--server-password={config["server-password"]}')

command.append(f'--battle-mode={config["battle-mode"]}')

if config['team-choosing']:
    command.append('--team-choosing')
else:
    command.append('--no-team-choosing')


subprocess.run(command)