import sys, os, json, urllib2, urllib, socket, logging, logging.handlers, time, datetime

class BGUpdate(object):
  def __init__(self):
    self.logger = logging.getLogger('bgupdate')
    self.logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler('bgupdate.log', 
                                                    maxBytes=2097152, 
                                                    backupCount=3,)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    self.logger.addHandler(handler)

  def set_status(self, status):
    self.logger.info(status)

  def is_playing_timeframe(self):
    now = datetime.datetime.now()
    if now > now.replace(hour=8, minute=30, second=0, microsecond=0):
      if now.weekday() == 6 and now > now.replace(hour=18, minute=01, second=0, microsecond=0):
        return False
      elif now > now.replace(hour=20, minute=58, second=0, microsecond=0):
        return False
      return True
    return False

  def download_file(self, url, file_name):
    try:
      self.set_status('downloading ' + file_name)
      u = urllib2.urlopen(url)
      f = open(file_name, 'wb')
      meta = u.info()
      file_size = int(meta.getheaders("Content-Length")[0])
      file_size_dl = 0
      block_sz = 64*1024
      while True:
        buffer = u.read(block_sz)
        if not buffer:
          break
        file_size_dl += len(buffer)
        f.write(buffer)
      f.close()
      return True
    except Exception as ex:
      self.set_status('error: %s' % ex)
      return False

  def start(self):
    self.set_status('bg update starting...')
    if not os.path.exists('content'):
      os.makedirs('content')

    while True:
      try:
        time.sleep(60*3) 
        if self.is_playing_timeframe():
          with open('data.json') as data_file:
            self.settings = json.load(data_file)
            if self.settings['Success'] == True:
              for row in self.settings['Items']:
                if row['LiveURL'] == True:
                  content_file = 'content/' + row['FileName']
                  self.download_file(row['Url'], content_file)
      except Exception as ex:
        self.set_status('error: %s' % ex)

bgupdate = BGUpdate()
bgupdate.start()