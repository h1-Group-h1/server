import requests

# requires a private api key from weatherbit.io
config_file = "api_key.txt"

with open(config_file, 'r') as f:
	API_KEY = f.read()

      
def get_weather(city, country, API_KEY):
    BASE_URL =  f'https://api.weatherbit.io/v2.0/current?city={city}&country={country}&&key={API_KEY}'
    
    print(BASE_URL)
    response = requests.get(BASE_URL)


    print(response.json())

    if response:
        data = (response.json())['data'][0]
        country = data['country_code']
        percent_clouds = data['clouds']
        sunset = data['sunset']
        sunrise = data['sunrise']
        current_temp = data['temp']
        feels_like = data['app_temp']
        lat = data['lat']
        lon = data['lon']
        
        
        result = {
            'country': country, 
            'cloud_cover': percent_clouds, 
            'sunset': sunset, 
            'sunrise': sunrise, 
            'temperature': current_temp, 
            'feelsLike': feels_like, 
            'latitude': lat, 
            'longitude': lon}

        return result
    else:
        print("Something went wrong.")
        
def get_location():
    base = dict(requests.get('https://ipinfo.io').json())
    
    city = base['city']
    country = base['country']

    return[city, country]


# example of how to get weather for your location
'''
my_city, my_country = get_location()

print(get_weather(my_city, my_country, API_KEY))
'''