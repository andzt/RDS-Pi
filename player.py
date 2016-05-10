import sys, os, datetime, time, json, multiprocessing, logging, logging.handlers, time, random, pyomxplayer, pexpect, subprocess
if sys.version_info[0] == 2:
    from Tkinter import *
else:
    from tkinter import *
from PIL import Image, ImageTk

class Status_Window:
  def __init__(self):
    self.tk = Tk()
    self.frame = Frame(self.tk, bg="black")
    self.frame.pack(fill="both", expand =1)
    self.canvas = Canvas(self.frame, bg="black", bd=0, highlightthickness=0)
    self.canvas.pack(fill="both", expand =1)
    self.canvas2 = Canvas(self.canvas, bg="black", bd=0, highlightthickness=0)
    self.canvas2.pack(fill="both", expand =1)
    self.state = False
    self.stopped = False
    self.toggle_fullscreen()
    self.loadingLabel = Label(self.tk, text="", fg="white", bg="black")
    self.loadingLabel.place(relx=0, rely=1, anchor=SW)
    self.tk.bind("<F11>", self.toggle_fullscreen)
    self.tk.bind("<Escape>", self.exit)
    self.logger = logging.getLogger('player')
    self.logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler('player.log', 
                                                    maxBytes=2097152, 
                                                    backupCount=3,)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    self.logger.addHandler(handler)
  
  def set_status(self, status):
    self.loadingLabel.config(text=status)

  def create_playlist(self, json):
    self.playlist = { 'list' : [] , 'ads' : [] }
    listRand = []
    listInter = { '1' : [], '2' : [], '3' : [], '4' : [] }

    for row in json['Items']:
      if row['EndDate'] is not None  and datetime.datetime.now() > datetime.datetime.strptime(row['EndDate'], "%Y-%m-%dT%H:%M:%S"):
        continue

      if row['Intersperse'] == True:
        if row['IntersperseFrequency'] == 1 or row['IntersperseFrequency'] == 2:
          listInter['2'].append(row)
        elif row['IntersperseFrequency'] == 3:
          listInter['3'].append(row)
        elif row['IntersperseFrequency'] == 4:
          listInter['4'].append(row)
      elif row['Randomize'] == True:
        listRand.append(row)

    random.shuffle(listRand)
    self.playlist['list'] = listRand
    self.playlist['ads'] = listInter

  def toggle_fullscreen(self, event=None):
    self.state = not self.state  # Just toggling the boolean
    self.tk.attributes("-fullscreen", self.state)
    return "break"

  def exit(self, event=None):
    self.state = False
    self.stopped = True
    self.tk.destroy()
    self.tk.attributes("-fullscreen", False)
    return "break"

  def play_video(self, path):
    player = pyomxplayer.OMXPlayer(path, None, True)
    while player.is_running():
      time.sleep(0.2)

  def play_image(self, path, duration):
    if duration > 0:
      size = (self.frame.winfo_width(), self.frame.winfo_height())
      image = Image.open(path)
      image = image.resize(size, Image.ANTIALIAS) #The (250, 250) is (height, width)
      resized = ImageTk.PhotoImage(image)
      
      self.canvas2.create_image(0,0, image=resized, anchor=NW)
      self.canvas2.image = resized
      self.tk.update()
      time.sleep(duration)
      self.canvas2.image = None
      self.canvas2.delete("all")
      self.tk.update()
    else:
      size = (self.frame.winfo_width(), self.frame.winfo_height())
      image = Image.open(path)
      image = image.resize(size, Image.ANTIALIAS) #The (250, 250) is (height, width)
      resized = ImageTk.PhotoImage(image)
      
      self.canvas2.create_image(0,0, image=resized, anchor=NW)
      self.canvas2.image = resized
      self.tk.update()
      while True:
        time.sleep(1000)
      self.canvas2.image = None
      self.canvas2.delete("all")
      self.tk.update()
      

  def play_image_1(self, path, duration):
    if duration > 0:
      cmd = "sudo fbi -T 2 -t %s -d /dev/fb0 -1 -noverbose -a '%s'" % (duration, path)
      self._image_process = pexpect.spawn(cmd)
      time.sleep(duration)
      self._image_process.close()
      self.killProcesses('fbi')
    else:
      cmd = "sudo fbi -T 2 -d /dev/fb0 -1 -noverbose -a '%s'" % path
      self._image_process = pexpect.spawn(cmd)  
      while True:
        time.sleep(1000)
      self._image_process.close()
      self.killProcesses('fbi')

  def play_website(self, path, duration):
    if duration > 0:
      self.b = pexpect.spawn('epiphany-browser %s' % path)
      time.sleep(1)
      time.sleep(duration)
      self.b.close()
    else:
      self.b = pexpect.spawn('epiphany-browser %s' % path)
      while True:
        time.sleep(1000)
      self.b.close()

  #def play_interlude(self):
    #fade in logo, time, temp
    #time.sleep(1)
    #fade out
  def killProcesses(self, filter):
    cmd = "sudo killall -q " + filter + " > /dev/null"
    #p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #out, err = p.communicate()
    os.system(cmd)

  def play_media(self, media):
    try:
      self.tk.update()
      self.logger.info('playing: %s' % media['Title'])
      if media['MediaType'] == 0:
        self.play_video('content/' + media['FileName'])
      elif media['MediaType'] == 1:
        self.play_image('content/' + media['FileName'], media['Duration'])
      elif media['MediaType'] == 2:
        self.play_website(media['Url'], media['Duration'])

    except Exception as ex:
      self.logger.error(ex)
    
    #play break
    #self.play_interlude()

  def play_list(self, fileList):
    if fileList is not None and len(fileList) > 0:
      for row in fileList:
        self.play_media(row)

  def start(self):
    try:
      self.logger.info('player start')
      with open('data.json') as data_file:
        self.create_playlist(json.load(data_file))
      
      count = 0
      while self.stopped == False:
        for row in self.playlist['list']:
          if self.stopped == True:
            break
          count = count + 1
          self.play_media(row)

          #play interspersed ads
          if count % 2 == 0:
            self.play_list(self.playlist['ads']['2'])
          if count % 3 == 0:
            self.play_list(self.playlist['ads']['3'])
          if count % 4 == 0:
            self.play_list(self.playlist['ads']['4'])

          self.play_list(self.playlist['ads']['1'])

    except Exception as ex:
      self.logger.error(ex)
    
    sys.exit('Abort')


window = Status_Window()
window.tk.after(3000, window.start)
window.tk.mainloop()