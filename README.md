## RDS-Pi

RDS-Pi is a digital signage program designed to be run on Raspberry Pis. This repository focuses specifically on the client code being run on the Pi. At a high level, the application allows high def video, images, and even websites to be displayed in a rotating or scheduled fashion.

Requires an API and scheduling site which will be uploaded in a separate repo at a later date...

## Pi 3 Setup Steps
### Raspi Configuration from Menu dropdown
- Expand filesystem
- Change password
- Change hostname
- Boot to Desktop on startup
- Wait for network on startup
- Overscan Enabled
- Interfaces - SSH Enabled (if you want to remotely login)
- Performance - Video GPU: 256
- Localisation: Set Locale to EN - USA
- Localisation: Set Timezone Area -CST or CDT
- Localisation: EN_US Keyboard
- Force HDMI as audio output

### Other
- Remove icons (trash)
- Auto-hide dock
- Background - fill with color only

### Always On Screen
- sudo nano /etc/lightdm/lightdm.conf

Add the following lines to the [SeatDefaults] section:

- xserver-command=X -s 0 dpms

### Updates and Libraries
- amixer set PCM - 0400
- sudo apt-get update
- sudo apt-get upgrade
- sudo apt-get install -y unclutter
- sudo apt-get install -y python-imaging
- sudo apt-get install -y python-imaging-tk
- sudo apt-get install -y python-pexpect
- sudo apt-get install -y fbi
- sudo apt-get install cec-utils

### Checkout git repo
- cd /home/pi
- git clone (repo_url)/pirds.git

### Set auto start script
- sudo nano ~/.config/lxsession/LXDE-pi/autostart
- @sh /home/pi/pirds/startup.sh


