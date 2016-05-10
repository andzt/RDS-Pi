import sys, os, datetime, time, platform, logging, logging.handlers, pexpect, atexit, json
from random import randint
import updater


class Manager(object):
  def __init__(self):
    self.id = platform.node()
    self.version = '1.0.1'
    
    self.api = '<API_URL>'
    # Set up a specific logger with our desired output level
    self.logger = logging.getLogger(self.id)
    self.logger.setLevel(logging.DEBUG)

    # Add the log message handler to the logger
    handler = logging.handlers.RotatingFileHandler('manager.log', 
                                                    maxBytes=2097152, 
                                                    backupCount=3,)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    self.logger.addHandler(handler)

  def set_status(self, status):
    self.logger.info(status)

  def start_monitor(self):
    try:
      self.set_status('start monitor...')
      os.system('echo on 0 | cec-client -s')
    except Exception as ex:
      self.set_status('error: %s' % ex)

  def turn_off_monitor(self):
    try:
      self.set_status('turn off monitor...')
      os.system('echo standby 0 | cec-client -s')
    except Exception as ex:
      self.set_status('error: %s' % ex)

  def shutdown(self):
    self.set_status('shutting down...')
    if hasattr(self, '_process') and self._process.isalive():
      self._process.terminate()
    if hasattr(self, '_bgprocess') and self._bgprocess.isalive():
      self._bgprocess.terminate()
    self.turn_off_monitor()
    os.system('shutdown now -h')

  def reboot(self):
    self.set_status('rebooting...')
    if hasattr(self, '_process') and self._process.isalive():
      self._process.terminate()
    os.system('reboot')

  def is_playing_timeframe(self):
    now = datetime.datetime.now()
    if hasattr(self.settings, 'ExtendedHours') and self.settings['ExtendedHours'] == True:
      if now > now.replace(hour=4, minute=28, second=0, microsecond=0):
        if now > now.replace(hour=22, minute=28, second=0, microsecond=0):
          return False
        return True
    else:
      if now > now.replace(hour=8, minute=48, second=0, microsecond=0):
        if now.weekday() == 6 and now > now.replace(hour=18, minute=01, second=0, microsecond=0):
          return False
        elif now > now.replace(hour=20, minute=58, second=0, microsecond=0):
          return False
        return True
    return False

  def check_player(self):
    if self.is_playing_timeframe():
      if not hasattr(self, '_process') or not self._process.isalive():
        self.set_status('starting player...')
        self.updater.ping_server('starting')
        self.start_monitor()
        self.start_player()
      else:
        # ping server to update status
        if self._process.isalive():
          self.updater.ping_server('playing')
        else:
          self.set_status('re-starting...')
          self.updater.ping_server('re-starting')
    else:
      if hasattr(self, '_process') and self._process.isalive():
        self._process.terminate()
      self.turn_off_monitor()
      self.set_status('idling')
      self.updater.ping_server('idle')

  def check_shutdown(self):
    now = datetime.datetime.now()
    if hasattr(self, 'settings') and 'PowerOn' in self.settings and self.settings['PowerOn'] == True:
      if now > now.replace(hour=4, minute=10, second=0, microsecond=0):
        if now < now.replace(hour=4, minute=15, second=0, microsecond=0):
          self.reboot()
      return
    
    #shut down
    if hasattr(self.settings, 'ExtendedHours') and self.settings['ExtendedHours'] == True:
      if now > now.replace(hour=22, minute=28, second=0, microsecond=0):
        self.updater.ping_server('daily-shutdown')
        self.shutdown()
    else:
      if now.weekday() == 6 and now > now.replace(hour=18, minute=01, second=0, microsecond=0):
        self.updater.ping_server('sunday-shutdown')
        self.shutdown()
      elif now > now.replace(hour=20, minute=58, second=0, microsecond=0):
        self.updater.ping_server('daily-shutdown')
        self.shutdown()

  def status_check(self):
    while True:
      try:
        self.check_player()
        self.check_shutdown()
 
      except Exception as ex:
        self.set_status('error: %s' % ex)

      rand = randint(0,120)
      time.sleep(180 + rand) 

  def run_update(self):
    try:
      self.updater = updater.Updater(self.id, self.api, self.set_status)
      self.set_status('starting update...')
      self.updater.ping_server('starting')
      self.updater.load_config()
      with open('data.json') as data_file:
        self.settings = json.load(data_file)
        if self.settings['Success'] == False:
          self.set_status('bad json file...')
          self.updater.ping_server('Error or no content')
      
      self.updater.sync_content()
    except Exception as ex:
      self.set_status('error: %s' % ex)

  def start_player(self):
    try:
      self.set_status('start player...')
      cmd = 'python player.py'
      self._process = pexpect.spawn(cmd)
    except Exception as ex:
      self.set_status('error: %s' % ex)

  def start_bgupdate(self):
    try:
      self.set_status('start bgupdate...')
      cmd = 'python bgupdate.py'
      self._bgprocess = pexpect.spawn(cmd)
    except Exception as ex:
      self.set_status('error: %s' % ex)

  def setup(self):
    self.set_status('starting manager setup...')
    self.run_update()
    self.start_bgupdate()
    self.status_check()     


def exit_handler():
  if hasattr(manager, '_process'):
    manager._process.terminate()
  if hasattr(manager, '_bgprocess'):
    manager._bgprocess.terminate()

atexit.register(exit_handler)
manager = Manager()
manager.setup()

