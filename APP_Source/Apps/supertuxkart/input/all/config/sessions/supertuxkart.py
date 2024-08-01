#!/usr/bin/env python3

import getsetup3
import subprocess

def get_config() -> dict:

    config = {}
    with getsetup3.Getsetup() as gs:
        config = {
            'windowmode': gs.getvalue('app.supertuxkart.options.windowmode'),
            'demo-mode': gs.getvalue('app.supertuxkart.options.demo-mode'),
            'connect-now': gs.getvalue('app.supertuxkart.options.connect-now'),
            'difficulty': gs.getvalue('app.supertuxkart.options.difficulty'),
            'mode': gs.getvalue('app.supertuxkart.options.mode'),
            'track': gs.getvalue('app.supertuxkart.options.track'),
            'kart': gs.getvalue('app.supertuxkart.options.kart'),
            'numkarts': gs.getvalue('app.supertuxkart.options.numkarts'),
            'laps': gs.getvalue('app.supertuxkart.options.laps')
        }
    return config


config = get_config()

command=['/services/supertuxkart/usr/games/supertuxkart']

if config['demo-mode'] != '0':
    command.append(f'--demo-mode={config["demo-mode"]}')

if config['connect-now']:
    command.append(f'--connect-now={config["connect-now"]}')

command.append(f'--difficulty={config["difficulty"]}')
command.append(f'--mode={config["mode"]}')

if config['numkarts'] != '0':
    command.append(f'--numkarts={config["numkarts"]}')

if config['laps'] != '0':
    command.append(f'--laps={config["laps"]}')

if config['windowmode'] != 'window':
    command.append('--fullscreen')

if config['track']:
    command.append(f'--track={config["track"]}')

if config['kart']:
    command.append(f'--kart={config["kart"]}')

subprocess.run(command)