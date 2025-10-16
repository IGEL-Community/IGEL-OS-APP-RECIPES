#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path
from shutil import copy2
import sys
import getsetup3 # type: ignore

# Create a logger
logger = logging.getLogger('demo')
logger.setLevel(logging.INFO)

app_part = '/services/cisco_secure_client'
setup_profile_dir_node = 'app.cisco_secure_client.config.profile_dir'

userhome_cisco = Path('/userhome/.cisco')
rw_part = Path('/services_rw/cisco_secure_client')
rw_profile_dir = rw_part / 'profile'
# add more dirs to link here; also add to config_mapper:
# rw_<custom>_dir: Path('<custom_path>')

config_mapper = {
  rw_profile_dir: Path(f'{app_part}/opt/cisco/secureclient/vpn/profile')
}

try:
  with getsetup3.Getsetup('ro') as setup:
    setup_profile_dir = setup.getvalue(setup_profile_dir_node)
    # add more directories from setupd params here:
    # <custom_dir> = setup.getvalue(<custom_dir_node>)
except getsetup3.SetupdError as err:
  # might have to handle this differently if more setupd nodes are added
  # to avoid a chrash if any of the parameter is missing
  sys.exit(err)


if Path(setup_profile_dir).exists():
  for profile_path in Path(setup_profile_dir).iterdir():
    profile_name = profile_path.name

    logger.info(f'Installing {profile_name} ..')

    rw_config_path: Path = rw_profile_dir / profile_name
    rw_profile_dir.mkdir(parents=True, exist_ok=True)

    copy2(profile_path, rw_config_path)

if userhome_cisco.exists():
  os.system(f'chown -R 777:100 {userhome_cisco}')

# link files stored on the rw partition to the corresponding location
for rw_dir in config_mapper:
  if not rw_dir.exists():
    continue
  for file in rw_dir.iterdir():
    profile_path: Path = config_mapper[rw_dir] / file.name
    if not profile_path.exists() and not profile_path.parent.samefile(file.parent):
      profile_path.symlink_to(file)
