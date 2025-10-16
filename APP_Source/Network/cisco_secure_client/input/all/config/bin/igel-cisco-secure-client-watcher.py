#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from systemd import journal
import logging
from pathlib import Path
from shutil import copy2
import sys
import getsetup3 # type: ignore
from watchdog.observers import Observer # type: ignore
from watchdog.events import FileSystemEventHandler # type: ignore
import dbus

class ConfigHandler(FileSystemEventHandler):
  def __init__(self):
    """
      Create custom handlers for each new config type, derived from this class.
      Simply override self.rw_config_dir and keep the rest.
      Example: class ProfileHandler(ConfigHandler)
    """
    self.rw_config_dir = Path('')

  def on_created(self, event):
    """ Copy the created file to the rw partition (rw_config_path) """
    config_path = Path(event.src_path)
    config_name = config_path.name
    rw_config_path: Path = self.rw_config_dir / config_name

    logger.info(f'Installing {config_name} ..')

    self.rw_config_dir.mkdir(parents=True, exist_ok=True)

    copy2(config_path, rw_config_path)

    service_name = 'igel-cisco-secure-client-config.service'

    try:
      # Connect to the system bus
      sysbus = dbus.SystemBus()
      systemd1 = sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
      manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')

      # Restart the service
      job = manager.RestartUnit(service_name, 'replace')

      print(f"Successfully restarted {service_name}")
    except dbus.exceptions.DBusException as err:
        logger.error(err)

  def on_deleted(self, event):
    """ Remove the corresponding file from the rw partition (rw_config_path). """
    config_path = Path(event.src_path)
    config_name = config_path.name
    rw_config_path: Path = self.rw_config_dir / config_name

    logger.info(f'Uninstalling {config_name} ..')

    rw_config_path.unlink(missing_ok=True)

class ProfileHandler(ConfigHandler):
   def __init__(self):
      super().__init__()
      self.rw_config_dir = Path('/services_rw/cisco_secure_client/profile')

# Create a logger
logger = logging.getLogger('demo')
logger.setLevel(logging.INFO)

# Add the JournaldLogHandler to the logger
logger.addHandler(journal.JournalHandler())

# setupd params to contain the directory paths to be watched:
# <custom_dir_node> = <custom_param_path>
setup_profile_dir_node = 'app.cisco_secure_client.config.profile_dir'

try:
  with getsetup3.Getsetup('ro') as setup:
    setup_profile_dir = setup.getvalue(setup_profile_dir_node)
    # add more directories from setupd params here:
    # <custom_dir> = setup.getvalue(<custom_dir_node>)
except getsetup3.SetupdError as err:
  # might have to handle this differently if more setupd nodes are added
  # to avoid a chrash if any of the parameter is missing
  sys.exit(err)

Path(setup_profile_dir).mkdir(exist_ok=True, parents=True)


observer = Observer()
observer.schedule(ProfileHandler(), path=setup_profile_dir, recursive=False)
# schedule more handlers here:
# observer.schedule(<custom_handler>(), path=<custom_dir>, recursive=False))
observer.start()

try:
    while observer.is_alive():
        observer.join(1)
finally:
    observer.stop()
    observer.join()

