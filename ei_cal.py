#!/usr/bin/python3

from PIL import Image,ImageDraw,ImageFont
import datetime
import dateutil.parser
import socket
from fractions import Fraction
import logging

import epd7in5

import g_cal
import draw_cal
import weather

def title(draw, today_dt, font, day_view_divider, title_divider):

    title = today_dt.strftime("%A %B %d, %Y")
    draw_cal.centered_text(draw, title, font, 0, 0, day_view_divider, title_divider, 0, 0)

def string_to_icon(weather_icon_text):

    icon_dict = {
        'clear-day': '\uf00d',
        'clear-night': '\uf02e',
        'rain': '\uf01d',
        'snow': '\uf01b',
        'sleet': '\uf0b5',
        'wind': '\uf021',
        'fog': '\uf014',
        'cloudy': '\uf013',
        'partly-cloudy-day': '\uf00c',
        'partly-cloudy-night': '\uf081'
    }
    return icon_dict.get(weather_icon_text, '\uf07b') #default output is 'N/A'

def moonphase_to_icon(moonphase):

    #find the nearest fraction of x/28 for decimal moonphase input
    moonphase_frac = Fraction(int(round(28*moonphase)),28)

    icon_dict = {
        Fraction(0,28) : '\uf0eb',
        Fraction(1,28) : '\uf0d0',
        Fraction(1,14) : '\uf0d1',
        Fraction(3,28) : '\uf0d2',
        Fraction(1,7) : '\uf0d3',
        Fraction(5,28) : '\uf0d4',
        Fraction(3,14) : '\uf0d5',
        Fraction(1,4) : '\uf0d6',
        Fraction(2,7) : '\uf0d7',
        Fraction(9,28) : '\uf0d8',
        Fraction(5,14) : '\uf0d9',
        Fraction(11,28) : '\uf0da',
        Fraction(3,7) : '\uf0dc',
        Fraction(13,28) : '\uf0dc',
        Fraction(1,2) : '\uf0dd',
        Fraction(15,28) : '\uf0de',
        Fraction(4,7) : '\uf0df',
        Fraction(17,28) : '\uf0e0',
        Fraction(9,14) : '\uf0e1',
        Fraction(19,28) : '\uf0e2',
        Fraction(5,7) : '\uf0e3',
        Fraction(3,4) : '\uf0e4',
        Fraction(11,14) : '\uf0e5',
        Fraction(23,28) : '\uf0e6',
        Fraction(6,7) : '\uf0e7',
        Fraction(25,28) : '\uf0e8',
        Fraction(13,14) : '\uf0e9',
        Fraction(27,28) : '\uf0ea',
    }
    return icon_dict.get(moonphase_frac, '\uf063') #default output is 'wi-dust'
    

def draw_weather_icons(draw, weather_data, left, top, right, bottom):

    icon_string = weather_data['weather_icon']
    icon = string_to_icon(icon_string)
    icon_font = ImageFont.truetype('./fonts/weathericons-regular-webfont.ttf', 64)
    draw_cal.centered_text(draw, icon, icon_font, left, top, right, bottom, 0, -12)

def today_weather_info(draw, weather_data, left, top, right, bottom):

    temp_now = weather_data['temp_now']
    precip_type = weather_data['precip_type']
    precip_prob = weather_data['precip_prob']
    temp_low = weather_data['temp_low']
    temp_high = weather_data['temp_high']

    weather_string = 'T: {} | {}% {} \nL: {} | H: {}'.format(temp_now, precip_type, precip_prob, temp_low, temp_high)
    font18 = ImageFont.truetype('./fonts/mononoki-Regular.ttf', 18)
    draw_cal.centered_text(draw, weather_string, font18, left, top, right, bottom, 6, -10)

def tmrw_weather_info(draw, weather_data, left, top, right, bottom):

    moonphase = weather_data['moonphase']
    moonphase_icon = moonphase_to_icon(moonphase)
    precip_type = weather_data['precip_type']
    precip_prob = weather_data['precip_prob']
    temp_low = weather_data['temp_low']
    temp_high = weather_data['temp_high']

    weather_string = 'M:   | {}% {} \n L: {} | H: {}'.format( precip_type, precip_prob, temp_low, temp_high)
    font18 = ImageFont.truetype('./fonts/mononoki-Regular.ttf', 18)
    draw_cal.centered_text(draw, weather_string, font18, left, top, right, bottom, 6, -10)
    #total hack to get the moonphase icon in
    moon_font = ImageFont.truetype('./fonts/weathericons-regular-webfont.ttf', 18)
    moon_string = '    {}            \n              '.format(moonphase_icon)
    draw_cal.centered_text(draw, moon_string, moon_font, left, top, right, bottom, -12, -10)


def main():

    logging.basicConfig(filename='ei_cal.log')

    #print('Getting Work Schedule')
    creds = g_cal.get_creds()
    '''
    if len(g_cal.get_events(creds)) == 0:
        print('No Work!')
    else:
        print(g_cal.get_events(creds))
    '''

    logging.info('Getting work events')
    try:
        work_events = g_cal.get_events(creds)
    except socket.timeout as e:
        work_events = []
        logging.exception(e)

    logging.info('Getting weather')
    API_KEY = weather.get_API_KEY('darksky.json')
    latitude, longitude = weather.get_lat_long('darksky.json')

    forecast = weather.get_forecast(API_KEY, latitude, longitude)
    weather_now = weather.get_weather_now(forecast)
    weather_tmrw = weather.get_weather_tmrw(forecast)

    epd = epd7in5.EPD()
    epd.init()
    epd.Clear()

    screen_w = epd.width
    screen_h = epd.height

    image = Image.new('1', (screen_w, screen_h), 255)

    logging.info('Drawing calendar')
    draw = ImageDraw.Draw(image)

    #center divider line
    day_view_divider = screen_w*5/9
    draw.line([(day_view_divider,0),(day_view_divider,screen_h)], fill=0, width=2)

    #draw calendar divider line
    cal_divider = screen_h/2
    draw.line([(0,cal_divider),(day_view_divider,cal_divider)], fill=0, width=2)

    #draw weather divider line
    title_divider = (screen_h - cal_divider)/5
    weather_divider = day_view_divider/2
    draw.line([(weather_divider, title_divider), (weather_divider, cal_divider)], fill=0, width=2)

    #draw weather icons 
    icon_divider = title_divider + (cal_divider-title_divider)*3/4
    draw_weather_icons(draw, weather_now, 0, title_divider, weather_divider, icon_divider)
    draw_weather_icons(draw, weather_tmrw, weather_divider, title_divider, day_view_divider, icon_divider)
    #draw.line([(0, icon_divider),(day_view_divider, icon_divider)], fill=0, width=2)

    #write weather info
    today_weather_info(draw, weather_now, 0, icon_divider, weather_divider, cal_divider)
    tmrw_weather_info(draw, weather_tmrw, weather_divider, icon_divider, day_view_divider, cal_divider)

    #get today as a datetime object
    today = datetime.date.today()

    #draw the date title
    font24 = ImageFont.truetype('./fonts/mononoki-Regular.ttf', 24)
    title(draw, today, font24, day_view_divider, title_divider)

    #draw the calendar in the lower left
    draw_cal.draw_cal(draw, screen_w, screen_h, day_view_divider, cal_divider, today)

    #draw the two day view on the right
    draw_cal.draw_two_day_view(draw, screen_w, screen_h, day_view_divider, 7, 17, today, work_events)

    logging.info('Send to e-ink screen')
    epd.display(epd.getbuffer(image))

    logging.info('Go to sleep')
    epd.sleep()

if __name__ == '__main__':
    main()
