import sys, os, json, urllib2, urllib, socket

class Updater(object):
  def __init__(self, id, api, status_callback):
    self.id = id
    self.api = api
    self.set_status = status_callback

  def load_config(self):
    config_url = self.api + 'list/' + self.id
    self.set_status('downloading config... ' + config_url)
    self.download_file(config_url, 'data.json')

  def sync_content(self):
    self.set_status('syncing content...')
    if not os.path.exists('content'):
      os.makedirs('content')

    with open('data.json') as data_file:
      self.settings = json.load(data_file)
      filenames = []
      if self.settings['Success'] == True:
        #sync new files
        for row in self.settings['Items']:
          if row['MediaType'] != 2:
            content_file = 'content/' + row['FileName']
            if not os.path.exists(content_file):
              success = self.download_file(row['Url'], content_file)
              if not success:
                #try again
                self.download_file(row['Url'], content_file)
            filenames.append(row['FileName'])

        #delete old files
        for filename in os.listdir('content'):
          if row['MediaType'] != 2:
            if filename not in filenames:
              os.remove('content/' + filename)

  def ping_server(self, status):
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("8.8.8.8",80))
      ip = s.getsockname()[0]
      s.close()
      mac = open('/sys/class/net/eth0/address').read()
      try:
        mac = open('/sys/class/net/wlan0/address').read()
      except Exception as mex:
        mac = open('/sys/class/net/eth0/address').read()



      url = self.api + 'update?id=' + self.id + '&ip=' + ip + '&mac=' + urllib.quote_plus(mac) + '&status=' + status


      data = urllib.urlencode({'id' : self.id,
                           'ip'  : ip, 'mac' : mac, 'status' : status})
      req = urllib2.Request(url, data)
      response = urllib2.urlopen(req)
      content = response.read()
    except Exception as ex:
      self.set_status('error: %s' % ex)

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

      fs = open(file_name, "rb")
      new_size = len(fs.read())
      fs.close()

      if new_size < file_size:
        os.remove(file_name)
        return False
      else:
        return True
    except Exception as ex:
      self.set_status('error: %s' % ex)
      os.remove(file_name)
      return False