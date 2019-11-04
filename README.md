# eink-cal

Insipred by several reddit posts, this is my take on the e-ink calendar display. 

## What's displayed
In the top left half is today's date and weather information. Left is today's weather forecast while right is tomorrow's. T is the current temperature (updated hourly). L and H are the day's low and high respectively. The precipitation chance defaults to rain%. M is the today's moonphase represented by icon. The white part of the icon is the illuminated portion of the moon. Moonphase is for today despite being on tomorrow's box. 

In the bottom left half is the calendar view. Shaded out regions is for days from the previous and upcoming months. A black box marks the current day.

Right half is the two day view showing work schedule which is pulled from Google calendar. Only pulls events titled "Work" for the time being, doesn't support whole day events, and doesn't support overlapping events. 

It takes about a minute for the script to update the e-ink screen so a clock functionality was not included or considered.

## How it works

* epd7in5.py and epdconfig.py are files provided by Waveshare that are necessary to interface with the e-ink
* g_cal.py searches for all events titled "Work" from today and tomorrow from Google Calendar
* weather.py gets the weather forecast for today and tomorrow from Darksky
* draw_cal.py defines some functions that are helpful for drawing different aspects of the calendar. It is also responsible for drawing the bottom left calendar view and right half two day view. 
* ei_cal.py ties the above scripts together and draws the top left of the screen (date, weather icons, weather info). 
* ei_cal_test.py functions exactly the same as ei_cal but instead of outputing the drawn image to the e-ink screen, it displays the drawn image to the default image viewer. Used for debugging on a computer. 
* quickstart.py is a lightly edited version of the one provided by Google in a tutorial mentioned below

## Hardware 

* Waveshare 7.5" e-ink Display with display driver HAT. Bought from [amazon](https://www.amazon.com/dp/B07DH55MGC/ref=cm_sw_r_tw_dp_U_x_gZhWDb2B86WGC).
* Raspberry Pi Zero WH. Bought from my local [Microcenter](https://www.microcenter.com/product/502843/raspberry-pi-zero-wh---with-pre-soldered-headers)
* 7"x5" picture frame. I just had one handy in my house but any 7"x5" frame should work. 

## Setup

Get a local clone of this project 

>git clone https://github.com/vwlau/eink-cal.git

### RPi Dependencies

In raspi-config make sure to enable SPI interface and that the localization settings are correct (correct timezone, etc). 

Contrary to [waveshare's documentation](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT) only the following are needed.

>sudo apt-get install python3-pip

>sudo pip3 install RPi.GPIO

>sudo pip3 install spidev

### Project Dependencies

After setting up the virtual environment, these are the required dependencies. 

>pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

>pip install tzlocal

>pip install darkskylib

>pip install python-dateutil

Pillow requires some extra dependencies accord to [this](https://www.techcoil.com/blog/how-to-setup-python-imaging-library-pillow-on-raspbian-stretch-lite-for-processing-images-on-your-raspberry-pi/)

>sudo apt-get install libjpeg-dev -y

>sudo apt-get install zlib1g-dev -y

>sudo apt-get install libfreetype6-dev -y

>sudo apt-get install liblcms1-dev -y

>sudo apt-get install libopenjp2-7 -y

>sudo apt-get install libtiff5 -y

>pip install Pillow

### Service and Timer Files

The eink-cal.service and eink-cal.timer files update the screen hourly. Move them to /etc/systemd/system

Update the service file line WorkingDirectory to wherever you cloned the project. Update the service file line ExecStart to your virtual environment directory. 

Service file required the use of WorkingDirectory so that the scripts call the correct file paths. Learned from [here](https://serverfault.com/a/821786). 

### Getting token.pickle

Follow step 1 to enable the google calendar api and download the client cofiguration files from this [tutorial](https://developers.google.com/calendar/quickstart/python). Then run quickstart.py as seen in the tutorial or g_cal.py on a machine with a web browser. After that, your token.pickle will be created. Send the token.pickle file to the rpi using SCP following this [tutorial](https://www.raspberrypi.org/documentation/remote-access/ssh/scp.md). 

### Create darksky.json 

Sign up for a Darksky developer account [here](https://darksky.net/dev) and get your secret key. Create a json file named 'darksky.json' with the following information in the project directory. 

`{
    "API_KEY": "Your_Secret_Key",  
    "latitude": "your lat",
    "longitude": "your long"
}`

## Starting the Service and Timers

>sudo systemctl daemon-reload

>sudo systemctl enable eink-cal.service

>sudo systemctl enable eink-cal.timer

>sudo systemctl start eink-cal.timer

To check status use:

>sudo systemctl status eink-cal.service

and/or

>systemctl list-timers --all
