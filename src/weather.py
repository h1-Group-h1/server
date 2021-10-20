import requests
# requires a private api key
config_file = "api_key.txt"

with open(config_file, 'r') as f:
	api_key = f.read()

      


def get_weather(search_city, api_key):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={search_city}&appid={api_key}'
    print(url)
    print(api_key)

    s = requests.Session()
    r = s.get(url)
    print(r.headers)
    print(r.text)

    result = requests.get(url)

    print(result)
    print(result.json())

    if result:
        json = result.json()
        city = json['name']
        country = json['sys']
        temp_kelvin = json['main']['temp']
        temp_celsius = temp_kelvin-273.15
        weather1 = json['weather'][0]['main']
        final = [city, country, temp_kelvin, 
                 temp_celsius, weather1]
        return final
    else:
        print("Something went wrong.")


my_city = dict(requests.get('https://ipinfo.io').json())['city']
print(my_city)
my_weather = get_weather(my_city.lower(), api_key)
print(my_weather)
