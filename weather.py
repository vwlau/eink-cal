from darksky import forecast
import json
#import datetime

def get_API_KEY(config_file):

    with open(config_file, "r") as read_file:
        config = json.load(read_file)
        return config['API_KEY']

def get_lat_long(config_file):

    with open(config_file, "r") as read_file:
        config= json.load(read_file)
        return config['latitude'], config['longitude'] 

def get_forecast(API_KEY, latitude, longitude):

    forecast_data = forecast(API_KEY, latitude, longitude)

    return forecast_data

def get_weather_now(forecast):

    weather_icon = forecast.icon

    #print(forecast.summary)
    temp_now = round(forecast.temperature)
    temp_low = round(forecast.daily[0].temperatureLow)
    temp_high = round(forecast.daily[0].temperatureHigh)
    if forecast.daily[0].precipIntensity == 0:
        precip_type = 'rain'
    else:
        precip_type = forecast.daily[0].precipType
    #precip_type = 'rain'
    precip_prob = round(forecast.precipProbability*100)
    #print('T: {} | L: {} | H: {} | P: {}%'.format(temp_now, temp_low, temp_high, precip_prob))

    weather_dict = {'weather_icon': weather_icon, 
                    'temp_now': temp_now, 
                    'temp_low': temp_low, 
                    'temp_high': temp_high, 
                    'precip_type': precip_type, 
                    'precip_prob': precip_prob}

    return weather_dict

def get_weather_tmrw(forecast):

    '''
    unix_time = forecast.daily[1].time
    print(datetime.datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d'))
    '''

    weather_icon = forecast.daily[1].icon

    #print(forecast.daily[1].summary)
    temp_low = round(forecast.daily[1].temperatureLow)
    temp_high = round(forecast.daily[1].temperatureHigh)
    if forecast.daily[0].precipIntensity == 0:
        precip_type = 'rain'
    else:
        precip_type = forecast.daily[0].precipType
    precip_prob = round(forecast.daily[1].precipProbability*100)
    #print('L: {} | H: {} | P: {}%'.format(temp_low, temp_high, precip_prob))

    moonphase = round(forecast.daily[0].moonPhase, 2)

    weather_dict = {'weather_icon': weather_icon, 
                    'temp_low': temp_low, 
                    'temp_high': temp_high, 
                    'precip_type': precip_type, 
                    'precip_prob': precip_prob, 
                    'moonphase': moonphase}

    return weather_dict

if __name__ == '__main__':

    forecast = get_forecast(get_API_KEY('darksky.json'), *get_lat_long('darksky.json'))
    get_weather_now(forecast)
    get_weather_tmrw(forecast)