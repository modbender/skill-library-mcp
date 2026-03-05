Title: Geocoding API

URL Source: http://openweathermap.org/api/geocoding-api?collection=other

Markdown Content:
Geocoding API
===============

To see the old version of the site [follow the link](https://old.openweathermap.org/)

![Image 1: Close](http://openweathermap.org/img/close-icon.svg)

*   [![Image 2: ow logo](http://openweathermap.org/payload/api/media/file/ow_logo.svg)](http://openweathermap.org/)
*       *   [Guide](http://openweathermap.org/guide)
    *   [APIs](http://openweathermap.org/api)
    *   Dashboard![Image 3: Dropdown icon](http://openweathermap.org/img/dropdown_icon.svg)
    *   [Pricing](http://openweathermap.org/price)
    *   [Marketplace](https://home.openweathermap.org/marketplace)
    *   [Maps](http://openweathermap.org/weathermap)
    *   [Initiatives](http://openweathermap.org/our-initiatives)
    *   [Blog](https://openweather.co.uk/blog)
    *   [Support](http://openweathermap.org/support-centre)
    *   [For Business](https://openweather.co.uk/)
    *   Search for...![Image 4: Search Icon](http://openweathermap.org/img/search.svg)

*       *   [Login](https://home.openweathermap.org/users/sign_in)
    *   [Join Today](https://home.openweathermap.org/users/sign_up)

[![Image 5: ow logo](http://openweathermap.org/payload/api/media/file/ow_logo.svg)](http://openweathermap.org/)

[Login](https://home.openweathermap.org/users/sign_in)

*   One Call API 3.0
*   Current & Forecast
*   Solar Irradiance
*   Historical
*   Maps
*   Environmental
*   Other

Other

*   
![Image 6: Dropdown icon](http://openweathermap.org/img/dropdown_icon.svg)Geocoding API
    *   [Product description](http://openweathermap.org/api/geocoding-api?collection=other&collection=other#description)
    *   
![Image 7: Dropdown icon](http://openweathermap.org/img/dropdown_icon.svg)Direct geocoding
        *   
![Image 8: Dropdown icon](http://openweathermap.org/img/dropdown_icon.svg)Coordinates by location name
            *   [How to make an API call](http://openweathermap.org/api/geocoding-api?collection=other&collection=other&collection=other&collection=other#direct_name_how)
            *   [Example of API response](http://openweathermap.org/api/geocoding-api?collection=other&collection=other&collection=other&collection=other#direct_name_example)
            *   [Fields in API response](http://openweathermap.org/api/geocoding-api?collection=other&collection=other&collection=other&collection=other#direct_name_fields)

        *   
![Image 9: Dropdown icon](http://openweathermap.org/img/dropdown_icon.svg)Coordinates by zip/post code
            *   [How to make an API call](http://openweathermap.org/api/geocoding-api?collection=other&collection=other&collection=other&collection=other#irect_zip_how)
            *   [Example of API response](http://openweathermap.org/api/geocoding-api?collection=other&collection=other&collection=other&collection=other#direct_zip_example)
            *   [Fields in API response](http://openweathermap.org/api/geocoding-api?collection=other&collection=other&collection=other&collection=other#direct_zip_fields)

    *   
![Image 10: Dropdown icon](http://openweathermap.org/img/dropdown_icon.svg)Reverse geocoding
        *   [How to make an API call](http://openweathermap.org/api/geocoding-api?collection=other&collection=other&collection=other#reverse_how)
        *   [Example of API response](http://openweathermap.org/api/geocoding-api?collection=other&collection=other&collection=other#reverse_example)
        *   [Fields in API response](http://openweathermap.org/api/geocoding-api?collection=other&collection=other&collection=other#reverse_fields)

*   
![Image 11: Dropdown icon](http://openweathermap.org/img/dropdown_icon.svg)Weather stations
    *   [Three simple steps](http://openweathermap.org/stations?collection=other&collection=other#steps)
    *   
![Image 12: Dropdown icon](http://openweathermap.org/img/dropdown_icon.svg)Basic methods to retrieve data from station
        *   [Register station](http://openweathermap.org/stations?collection=other&collection=other&collection=other#create_station)
        *   [Send measurements for station](http://openweathermap.org/stations?collection=other&collection=other&collection=other#measurements)
        *   [Get measurements for station](http://openweathermap.org/stations?collection=other&collection=other&collection=other#get_measurements)

    *   
![Image 13: Dropdown icon](http://openweathermap.org/img/dropdown_icon.svg)Additional features
        *   [Get all stations](http://openweathermap.org/stations?collection=other&collection=other&collection=other#get_stations)
        *   [Get station info](http://openweathermap.org/stations?collection=other&collection=other&collection=other#get_station)
        *   [Update station info](http://openweathermap.org/stations?collection=other&collection=other&collection=other#update_station)
        *   [Delete station](http://openweathermap.org/stations?collection=other&collection=other&collection=other#delete_station)

    *   [Possible errors](http://openweathermap.org/stations?collection=other&collection=other#errors)

Geocoding API

Geocoding API is a simple tool that we have developed to ease the search for locations while working with geographic names and coordinates.

Supporting API calls by geographical coordinates is the most accurate way to specify any location, that is why this method is integrated in all OpenWeather APIs. However, this way is not always suitable for all users. Geocoding is the process of transformation of any location name into geographical coordinates, and the other way around (reverse geocoding). OpenWeather’s Geocoding API supports both the direct and reverse methods, working at the level of city names, areas and districts, countries and states:

*   [Direct geocoding](http://openweathermap.org/api/geocoding-api?collection=other#direct) converts the specified name of a location or zip/post code into the exact geographical coordinates;
*   [Reverse geocoding](http://openweathermap.org/api/geocoding-api?collection=other#reverse) converts the geographical coordinates into the names of the nearby locations.

Direct geocoding

Direct geocoding allows to get geographical coordinates (lat, lon) by using name of the location (city name or area name). If you use the `limit` parameter in the API call, you can cap how many locations with the same name will be seen in the API response (for instance, London in the UK and London in the US).

### Coordinates by location name

### How to make an API call

API call
--------

`http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key}`

![Image 14: Copy Icon](http://openweathermap.org/img/copy_icon.svg)

| Parameters |
| --- |
| `q` | required | City name, state code (only for the US) and country code divided by comma. Please use ISO 3166 country codes. |
| `appid` | required | Your unique API key (you can always find it on your account page under the ["API key" tab](https://home.openweathermap.org/api_keys)) |
| `limit` | optional | Number of the locations in the API response (up to 5 results can be returned in the API response) |

Example of API call
-------------------

`http://api.openweathermap.org/geo/1.0/direct?q=London&limit=5&appid={API key}`

![Image 15: Copy Icon](http://openweathermap.org/img/copy_icon.svg)

Example of API response
-----------------------

`To view the API response, expand the example by clicking the triangle.`

![Image 16: Toggle](http://openweathermap.org/img/dropdown_icon.svg)![Image 17: Copy Icon](http://openweathermap.org/img/copy_icon.svg)

Please note that the fields present will vary based on a country to which a location belongs as well as a specific location.

*   `name` Name of the found location
*   `local_names`
    *   `local_names.[language code]` Name of the found location in different languages. The list of names can be different for different locations
    *   `local_names.ascii` Internal field
    *   `local_names.feature_name` Internal field

*   `lat` Geographical coordinates of the found location (latitude)
*   `lon` Geographical coordinates of the found location (longitude)
*   `country` Country of the found location
*   `state`(where available) State of the found location

### Coordinates by zip/post code

How to make an API call
-----------------------

`http://api.openweathermap.org/geo/1.0/zip?zip={zip code},{country code}&appid={API key}`

![Image 18: Copy Icon](http://openweathermap.org/img/copy_icon.svg)

| Parameters |
| --- |
| `zip code` | required | Zip/post code and country code divided by comma. Please use ISO 3166 country codes. |
| `appid` | required | Your unique API key (you can always find it on your account page under the ["API key" tab](https://home.openweathermap.org/api_keys)) |

Example of API call
-------------------

`http://api.openweathermap.org/geo/1.0/zip?zip=E14,GB&appid={API key}`

![Image 19: Copy Icon](http://openweathermap.org/img/copy_icon.svg)

Example of API response
-----------------------

```
{
  "zip": "90210",
  "name": "Beverly Hills",
  "lat": 34.0901,
  "lon": -118.4065,
  "country": "US"
}
```

![Image 20: Toggle](http://openweathermap.org/img/dropdown_icon.svg)![Image 21: Copy Icon](http://openweathermap.org/img/copy_icon.svg)

### Fields in API response

*   `zip` Specified zip/post code in the API request
*   `name` Name of the found area
*   `lat` Geographical coordinates of the centroid of found zip/post code (latitude)
*   `lon` Geographical coordinates of the centroid of found zip/post code (longitude)
*   `country` Country of the found zip/post code

Reverse geocoding

Reverse geocoding allows to get name of the location (city name or area name) by using geografical coordinates (lat, lon). The `limit` parameter in the API call allows you to cap how many location names you will see in the API response.

API call
--------

`http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit={limit}&appid={API key}`

![Image 22: Copy Icon](http://openweathermap.org/img/copy_icon.svg)

| Parameters |
| --- |
| `lat, lon` | required | Geographical coordinates (latitude, longitude) |
| `appid` | required | Your unique API key (you can always find it on your account page under the ["API key" tab](https://home.openweathermap.org/api_keys)) |
| `limit` | optional | Number of the location names in the API response (several results can be returned in the API response) |

Example of API call
-------------------

`http://api.openweathermap.org/geo/1.0/reverse?lat=51.5098&lon=-0.1180&limit=5&appid={API key}`

![Image 23: Copy Icon](http://openweathermap.org/img/copy_icon.svg)

Example of API response
-----------------------

`To view the API response, expand the example by clicking the triangle.`

![Image 24: Toggle](http://openweathermap.org/img/dropdown_icon.svg)![Image 25: Copy Icon](http://openweathermap.org/img/copy_icon.svg)

Please note that the fields present will vary based on a country to which a location belongs as well as a specific location.

*   `name` Name of the found location
*   `local_names`
    *   `local_names.[language code]` Name of the found location in different languages. The list of names can be different for different locations.
    *   `local_names.ascii` Internal field
    *   `local_names.feature_name` Internal field

*   `lat` Geographical coordinates of the found location (latitude)
*   `lon` Geographical coordinates of the found location (longitude)
*   `country` Country of the found location
*   `state`(where available) State of the found location

Build smarter, plan better with the world’s most flexible weather data platform
===============================================================================

Build smarter, plan better with the world’s most flexible weather data platform

*   [Get Api Key](https://home.openweathermap.org/users/sign_in)
*   [Explore Api Docs](http://openweathermap.org/api/one-call-3)

Products

*   [Current and Forecast APIs](http://openweathermap.org/api#current)
*   [Historical Weather Data](http://openweathermap.org/api#history)
*   [Weather Maps](http://openweathermap.org/api#maps)
*   [Weather Dashboard](https://dashboard.openweather.co.uk/)
*   [Widgets](http://openweathermap.org/widgets-constructor)

Subscription

*   [How to start](http://openweathermap.org/appid)
*   [Pricing](http://openweathermap.org/price)
*   [Subscribe for free](https://home.openweathermap.org/)
*   [FAQ](http://openweathermap.org/faq)

Technologies

*   [Our technology](http://openweathermap.org/technology)
*   [Accuracy and quality of weather data](https://openweather.co.uk/accuracy-and-quality)
*   [Connect your weather station](http://openweathermap.org/stations)

[Offices](http://openweathermap.org/about/our-offices)

*   London, UK

The Gherkin,30 St Mary`s Axe, The City Of London, London EC3A 8BF,United Kingdom

*   Paphos, Cyprus

Gladstonos 12-14,Office 1 Hugge Space,Paphos 8046, Cyprus

*   Delaware, US

16192 Coastal Highway,Lewes, Delaware 19958,United States

*   [![Image 26: App Store](http://openweathermap.org/payload/api/media/file/App_Store.svg)](https://apps.apple.com/gb/app/openweather/id1535923697)
*   [![Image 27: Google Play](http://openweathermap.org/payload/api/media/file/Google_Play.svg)](https://play.google.com/store/apps/details?id=uk.co.openweather)

*   [![Image 28: Instagram icon](http://openweathermap.org/payload/api/media/file/instagram-logo.svg)](https://www.instagram.com/openweathermap?igsh=OTRsOWs1aDh2bmNu)
*   [![Image 29: Facebook icon](http://openweathermap.org/payload/api/media/file/facebook-logo.svg)](https://www.facebook.com/groups/270748973021342)
*   [![Image 30: Telegram icon](http://openweathermap.org/payload/api/media/file/telegram-logo.svg)](https://t.me/openweathermap)
*   [![Image 31: LinkedIn icon](http://openweathermap.org/payload/api/media/file/Vector_(5).svg)](https://www.linkedin.com/company/9816754)
*   [![Image 32: Medium icon](http://openweathermap.org/payload/api/media/file/medium-logo.svg)](https://medium.com/@openweathermap)
*   [![Image 33: GitHub icon](http://openweathermap.org/payload/api/media/file/github-logo.svg)](https://github.com/openweathermap)
*   [![Image 34: Discord icon](http://openweathermap.org/payload/api/media/file/discord.svg)](https://discord.com/invite/YyPZCXb4Jq)

*   ![Image 35: ISO 9001](http://openweathermap.org/_next/image?url=%2Fpayload%2Fapi%2Fmedia%2Ffile%2Fiso-9001.png&w=3840&q=75)
*   ![Image 36: ISO 27001](http://openweathermap.org/_next/image?url=%2Fpayload%2Fapi%2Fmedia%2Ffile%2Fiso-27001.jpg&w=3840&q=75)
*   ![Image 37: CNB Business Logo](http://openweathermap.org/_next/image?url=%2Fpayload%2Fapi%2Fmedia%2Ffile%2FCNB_Business_Logo_2024-1.png&w=3840&q=75)
*   ![Image 38: RMets Logo](http://openweathermap.org/_next/image?url=%2Fpayload%2Fapi%2Fmedia%2Ffile%2FRMets_Logo_corp.png&w=3840&q=75)
*   ![Image 39: ESPO logo](http://openweathermap.org/_next/image?url=%2Fpayload%2Fapi%2Fmedia%2Ffile%2F_espo_logo.png&w=3840&q=75)
*   ![Image 40: LCRIG logo](http://openweathermap.org/_next/image?url=%2Fpayload%2Fapi%2Fmedia%2Ffile%2Flcrig_logo.png&w=3840&q=75)

Company

OpenWeather is a team of IT experts and data scientists that has been practising deep weather data science. For each point on the globe, OpenWeather provides historical, current and forecasted weather data via light-speed APIs. Headquarters in London, UK.

Supplier of Achilles UVDB community

© 2012 - 2026 OpenWeather ® All rights reserved

*   [Terms & conditions of sale](https://openweather.co.uk/api/files/file/OpenWeather_T%26C_of_sale.pdf)
*   [Website terms & conditions](https://openweather.co.uk/api/files/file/Openweather_website_terms_and_conditions_of_use.pdf)
*   [Privacy policy](https://openweather.co.uk/privacy-policy)

![Image 41](http://openweathermap.org/img/mdi_message-fast.svg)

Title: Current weather data

URL Source: http://openweathermap.org/current?collection=current_forecast

Markdown Content:
Current weather data

### Product concept

Access current weather data for any location on Earth! We collect and process weather data from different sources such as global and local weather models, satellites, radars and a vast network of weather stations. Data is available in JSON, XML, or HTML format.

Call current weather data

How to make an API call
-----------------------

`https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}`

| Parameters |
| --- |
| `lat` | required | Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our [Geocoding API](https://openweathermap.org/api/geocoding-api) |
| `lon` | required | Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our [Geocoding API](https://openweathermap.org/api/geocoding-api) |
| `appid` | required | Your unique API key (you can always find it on your account page under the ["API key" tab](https://home.openweathermap.org/api_keys)) |
| `mode` | optional | Response format. Possible values are `xml` and `html`. If you don't use the `mode` parameter format is JSON by default. [Learn more](http://openweathermap.org/current?collection=current_forecast#format) |
| `units` | optional | Units of measurement. `standard`, `metric` and `imperial` units are available. If you do not use the `units` parameter, `standard` units will be applied by default. [Learn more](http://openweathermap.org/current?collection=current_forecast#data) |
| `lang` | optional | You can use this parameter to get the output in your language. [Learn more](http://openweathermap.org/current?collection=current_forecast#multi) |

Please use [Geocoder API](https://openweathermap.org/api/geocoding-api) if you need automatic convert city names and zip-codes to geo coordinates and the other way around.

Please note that [built-in geocoder](http://openweathermap.org/current?collection=current_forecast#geocoding) has been deprecated. Although it is still available for use, bug fixing and updates are no longer available for this functionality.

Examples of API calls
---------------------

`https://api.openweathermap.org/data/2.5/weather?lat=44.34&lon=10.99&appid={API key}`

```
{
  "coord": {
    "lon": 10.99,
    "lat": 44.34
  },
  "weather": [
    {
      "id": 501,
      "main": "Rain",
      "description": "moderate rain",
      "icon": "10d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 298.48,
    "feels_like": 298.74,
    "temp_min": 297.56,
    "temp_max": 300.05,
    "pressure": 1015,
    "humidity": 64,
    "sea_level": 1015,
    "grnd_level": 933
  },
  "visibility": 10000,
  "wind": {
    "speed": 0.62,
    "deg": 349,
    "gust": 1.18
  },
  "rain": {
    "1h": 3.16
  },
  "clouds": {
    "all": 100
  },
  "dt": 1661870592,
  "sys": {
    "type": 2,
    "id": 2075663,
    "country": "IT",
    "sunrise": 1661834187,
    "sunset": 1661882248
  },
  "timezone": 7200,
  "id": 3163858,
  "name": "Zocca",
  "cod": 200
}
```

API response

If you do not see some of the parameters in your API response it means that these weather phenomena are just not happened for the time of measurement for the city or location chosen. Only really measured or calculated data is displayed in API response.

JSON
----

```
{
   "coord": {
      "lon": 7.367,
      "lat": 45.133
   },
   "weather": [
      {
         "id": 501,
         "main": "Rain",
         "description": "moderate rain",
         "icon": "10d"
      }
   ],
   "base": "stations",
   "main": {
      "temp": 284.2,
      "feels_like": 282.93,
      "temp_min": 283.06,
      "temp_max": 286.82,
      "pressure": 1021,
      "humidity": 60,
      "sea_level": 1021,
      "grnd_level": 910
   },
   "visibility": 10000,
   "wind": {
      "speed": 4.09,
      "deg": 121,
      "gust": 3.47
   },
   "rain": {
      "1h": 2.73
   },
   "clouds": {
      "all": 83
   },
   "dt": 1726660758,
   "sys": {
      "type": 1,
      "id": 6736,
      "country": "IT",
      "sunrise": 1726636384,
      "sunset": 1726680975
   },
   "timezone": 7200,
   "id": 3165523,
   "name": "Province of Turin",
   "cod": 200
}
```

### JSON format API response fields

*   `coord`

    *   `coord.lon`Longitude of the location
    *   `coord.lat`Latitude of the location

*   `weather`(more info[Weather condition codes](https://openweathermap.org/weather-conditions))

    *   `weather.id`Weather condition id
    *   `weather.main`Group of weather parameters (Rain, Snow, Clouds etc.)
    *   `weather.description`Weather condition within the group. Please find more[here.](https://openweathermap.org/current#list)You can get the output in your language.[Learn more](https://openweathermap.org/current#multi)
    *   `weather.icon`Weather icon id

*   `base`Internal parameter
*   `main`

    *   `main.temp`Temperature. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit
    *   `main.feels_like`Temperature. This temperature parameter accounts for the human perception of weather. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit
    *   `main.pressure`Atmospheric pressure on the sea level, hPa
    *   `main.humidity`Humidity, %
    *   `main.temp_min`Minimum temperature at the moment. This is minimal currently observed temperature (within large megalopolises and urban areas). Please find more info[here.](https://openweathermap.org/current#min)Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit
    *   `main.temp_max`Maximum temperature at the moment. This is maximal currently observed temperature (within large megalopolises and urban areas). Please find more info[here.](https://openweathermap.org/current#min)Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit
    *   `main.sea_level`Atmospheric pressure on the sea level, hPa
    *   `main.grnd_level`Atmospheric pressure on the ground level, hPa

*   `visibility`Visibility, meter. The maximum value of the visibility is 10 km
*   `wind`

    *   `wind.speed`Wind speed. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour
    *   `wind.deg`Wind direction, degrees (meteorological)
    *   `wind.gust`Wind gust. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour

*   `clouds`

    *   `clouds.all`Cloudiness, %

*   `rain`

    *   `1h`(where available)Precipitation, mm/h. Please note that only mm/h as units of measurement are available for this parameter

*   `snow`

    *   `1h`(where available)Precipitation, mm/h. Please note that only mm/h as units of measurement are available for this parameter

*   `dt`Time of data calculation, unix, UTC
*   `sys`

    *   `sys.type`Internal parameter
    *   `sys.id`Internal parameter
    *   `sys.message`Internal parameter
    *   `sys.country`Country code (GB, JP etc.)
    *   `sys.sunrise`Sunrise time, unix, UTC
    *   `sys.sunset`Sunset time, unix, UTC

*   `timezone`Shift in seconds from UTC
*   `id`City ID. Please note that built-in geocoder functionality has been deprecated. Learn more[here](https://openweathermap.org/current#builtin)
*   `name`City name. Please note that built-in geocoder functionality has been deprecated. Learn more[here](https://openweathermap.org/current#builtin)
*   `cod`Internal parameter

XML

Example of API response
-----------------------

```
<current>
    <city id="3163858" name="Zocca">
    <coord lon="10.99" lat="44.34"/>
    <country>IT</country>
    <timezone>7200</timezone>
    <sun rise="2022-08-30T04:36:27" set="2022-08-30T17:57:28"/>
    </city>
    <temperature value="298.48" min="297.56" max="300.05" unit="kelvin"/>
    <feels_like value="298.74" unit="kelvin"/>
    <humidity value="64" unit="%"/>
    <pressure value="1015" unit="hPa"/>
    <wind>
    <speed value="0.62" unit="m/s" name="Calm"/>
    <gusts value="1.18"/>
    <direction value="349" code="N" name="North"/>
    </wind>
    <clouds value="100" name="overcast clouds"/>
    <visibility value="10000"/>
    <precipitation value="3.37" mode="rain" unit="1h"/>
    <weather number="501" value="moderate rain" icon="10d"/>
    <lastupdate value="2022-08-30T14:45:57"/>
</current>
```

### XML format API response fields

*   `city`

    *   `city.id`City ID. Please note that built-in geocoder functionality has been deprecated. Learn more[here](https://openweathermap.org/current#builtin)
    *   `city.name`City name. Please note that built-in geocoder functionality has been deprecated. Learn more[here](https://openweathermap.org/current#builtin)
    *   `city.coord`
    

        *   `city.coord.lon`Geo location, longitude
        *   `city.coord.lat`Geo location, latitude

    *   `city.country`Country code (GB, JP etc.). Please note that built-in geocoder functionality has been deprecated. Learn more[here](https://openweathermap.org/current#builtin)
    *   `timezone`Shift in seconds from UTC
    *   `city.sun`
    

        *   `city.sun.rise`Sunrise time
        *   `city.sun.set`Sunset time

*   `temperature`

    *   `temperature.value`Temperature
    *   `temperature.min`Minimum temperature at the moment of calculation. This is minimal currently observed temperature (within large megalopolises and urban areas), use this parameter optionally. Please find more info[here](https://openweathermap.org/current#min)
    *   `temperature.max`Maximum temperature at the moment of calculation. This is maximal currently observed temperature (within large megalopolises and urban areas), use this parameter optionally. Please find more info[here](https://openweathermap.org/current#min)
    *   `temperature.unit`Unit of measurements. Possible value is Celsius, Kelvin, Fahrenheit

*   `feels_like`

    *   `feels_like.value`Temperature. This temperature parameter accounts for the human perception of weather
    *   `feels_like.unit`Unit of measurements. Possible value is Celsius, Kelvin, Fahrenheit. Unit Default: Kelvin

*   `humidity`

    *   `humidity.value`Humidity value
    *   `humidity.unit`Humidity units, %

*   `pressure`

    *   `pressure.value`Pressure value
    *   `pressure.unit`Pressure units, hPa

*   `wind`

    *   `wind.speed`
    

        *   `wind.speed.value`Wind speed
        *   `wind.speed.unit`Wind speed units, m/s
        *   `wind.speed.name`Type of the wind

    *   `wind.direction`
    

        *   `wind.direction.value`Wind direction, degrees (meteorological)
        *   `wind.direction.code`Code of the wind direction. Possible value is WSW, N, S etc.
        *   `wind.direction.name`Full name of the wind direction

*   `clouds`

    *   `clouds.value`Cloudiness
    *   `clouds.name`Name of the cloudiness

*   `visibility`

    *   `visibility.value`Visibility, meter. The maximum value of the visibility is 10 km

*   `precipitation`

    *   `precipitation.value`Precipitation, mm. Please note that only mm as units of measurement are available for this parameter.
    *   `precipitation.mode`Possible values are 'no", name of weather phenomena as 'rain', 'snow'

*   `weather`

    *   `weather.number`Weather condition id
    *   `weather.value`Weather condition name
    *   `weather.icon`Weather icon id

*   `lastupdate`

    *   `lastupdate.value`Last time when data was updated

List of weather condition codes

Min/max temperature in current weather API and forecast API

Please do not confuse min/max parameters in our weather APIs.

*   In **Current weather API**, [Hourly forecast API](https://openweathermap.org/api/hourly-forecast) and [5 day / 3 hour forecast API](https://openweathermap.org/forecast5) - **temp_min** and **temp_max** are optional parameters mean min / max temperature in the city at the current moment just for your reference. For large cities and megalopolises geographically expanded it might be applicable. In most cases both **temp_min** and **temp_max** parameters have the same volume as 'temp'. Please use **temp_min** and **temp_max** parameters in current weather API optionally.
*   In [16 Day forecast](https://openweathermap.org/forecast16) - **min** and **max** mean maximum and minimum temperature in the day.

Example of current weather API response
---------------------------------------

```
"main":{
     "temp":306.15, //current temperature
     "pressure":1013,
     "humidity":44,
     "temp_min":306.15, //min current temperature in the city
     "temp_max":306.15 //max current temperature in the city
   }
```

Example of daily forecast weather API response
----------------------------------------------

```
"dt":1406080800,
  "temp":{
        "day":297.77,  //daily averaged temperature
        "min":293.52, //daily min temperature
        "max":297.77, //daily max temperature
        "night":293.52, //night temperature
        "eve":297.77, //evening temperature
        "morn":297.77}, //morning temperature
```

Bulk downloading

We provide number of bulk files with current weather and forecasts. The service allows you to regularly download current weather and forecast data in JSON format. There is no need to call an API to do this.

More information is on the [Bulk page](https://openweathermap.org/bulk).

### Examples of bulk files

Other features

### Geocoding API

Requesting API calls by geographical coordinates is the most accurate way to specify any location. If you need to convert city names and zip-codes to geo coordinates and the other way around automatically, please use our [Geocoding API](https://openweathermap.org/api/geocoding-api).

### Built-in geocoding

Please use [Geocoder API](https://openweathermap.org/api/geocoding-api) if you need automatic convert city names and zip-codes to geo coordinates and the other way around.

**Please note that API requests by city name, zip-codes and city id have been deprecated. Although they are still available for use, bug fixing and updates are no longer available for this functionality.**

### Built-in API request by city name

You can call by city name or city name, state code and country code. Please note that searching by states available only for the USA locations.

API call
--------

`https://api.openweathermap.org/data/2.5/weather?q={city name}&appid={API key}`

API call
--------

`https://api.openweathermap.org/data/2.5/weather?q={city name},{country code}&appid={API key}`

API call
--------

`https://api.openweathermap.org/data/2.5/weather?q={city name},{state code},{country code}&appid={API key}`

| Parameters |
| --- |
| `q` | required | City name, state code and country code divided by comma, Please refer to [ISO 3166](https://www.iso.org/obp/ui/#search) for the state codes or country codes. You can specify the parameter not only in English. In this case, the API response should be returned in the same language as the language of requested location name if the location is in our predefined list of more than 200,000 locations. |
| `appid` | required | Your unique API key (you can always find it on your account page under the ["API key" tab](https://home.openweathermap.org/api_keys)) |
| `mode` | optional | Response format. Possible values are `xml` and `html`. If you don't use the `mode` parameter format is JSON by default. [Learn more](http://openweathermap.org/current?collection=current_forecast#format) |
| `units` | optional | Units of measurement. `standard`, `metric` and `imperial` units are available. If you do not use the `units` parameter, `standard` units will be applied by default. [Learn more](http://openweathermap.org/current?collection=current_forecast#data) |
| `lang` | optional | You can use this parameter to get the output in your language. [Learn more](http://openweathermap.org/current?collection=current_forecast#multi) |

Examples of API calls:
----------------------

```
{
     "coord": {
       "lon": -0.13,
       "lat": 51.51
     },
     "weather": [
       {
         "id": 300,
         "main": "Drizzle",
         "description": "light intensity drizzle",
         "icon": "09d"
       }
     ],
     "base": "stations",
     "main": {
       "temp": 280.32,
       "pressure": 1012,
       "humidity": 81,
       "temp_min": 279.15,
       "temp_max": 281.15
     },
     "visibility": 10000,
     "wind": {
       "speed": 4.1,
       "deg": 80
     },
     "clouds": {
       "all": 90
     },
     "dt": 1485789600,
     "sys": {
       "type": 1,
       "id": 5091,
       "message": 0.0103,
       "country": "GB",
       "sunrise": 1485762037,
       "sunset": 1485794875
     },
     "id": 2643743,
     "name": "London",
     "cod": 200
     }
```

Example of API response
-----------------------

```
{
     "coord": {
       "lon": -0.13,
       "lat": 51.51
     },
     "weather": [
       {
         "id": 300,
         "main": "Drizzle",
         "description": "light intensity drizzle",
         "icon": "09d"
       }
     ],
     "base": "stations",
     "main": {
       "temp": 280.32,
       "pressure": 1012,
       "humidity": 81,
       "temp_min": 279.15,
       "temp_max": 281.15
     },
     "visibility": 10000,
     "wind": {
       "speed": 4.1,
       "deg": 80
     },
     "clouds": {
       "all": 90
     },
     "dt": 1485789600,
     "sys": {
       "type": 1,
       "id": 5091,
       "message": 0.0103,
       "country": "GB",
       "sunrise": 1485762037,
       "sunset": 1485794875
     },
     "id": 2643743,
     "name": "London",
     "cod": 200
     }
```

There is a possibility to receive a central district of the city/town with its own parameters (geographic coordinates/id/name) in API response. [Example](http://samples.openweathermap.org/data/2.5/forecast?q=M%C3%BCnchen,DE&appid=439d4b804bc8187953eb36d2a8c26a02)

### Built-in API request by city ID

You can make an API call by city ID. List of city ID 'city.list.json.gz' can be downloaded [here](http://bulk.openweathermap.org/sample/).

We recommend to call API by city ID to get unambiguous result for your city.

API call
--------

`https://api.openweathermap.org/data/2.5/weather?id={city id}&appid={API key}`

| Parameters |
| --- |
| `id` | required | City ID. List of city ID 'city.list.json.gz' can be downloaded [here](http://bulk.openweathermap.org/sample/). |
| `appid` | required | Your unique API key (you can always find it on your account page under the ["API key" tab](https://home.openweathermap.org/api_keys)) |
| `mode` | optional | Response format. Possible values are `xml` and `html`. If you don't use the `mode` parameter format is JSON by default. [Learn more](http://openweathermap.org/current?collection=current_forecast#format) |
| `units` | optional | Units of measurement. `standard`, `metric` and `imperial` units are available. If you do not use the `units` parameter, `standard` units will be applied by default. [Learn more](http://openweathermap.org/current?collection=current_forecast#data) |
| `lang` | optional | You can use this parameter to get the output in your language. [Learn more](http://openweathermap.org/current?collection=current_forecast#multi) |

Examples of API calls
---------------------

```
{
     "coord": {
       "lon": 145.77,
       "lat": -16.92
     },
     "weather": [
       {
         "id": 802,
         "main": "Clouds",
         "description": "scattered clouds",
         "icon": "03n"
       }
     ],
     "base": "stations",
     "main": {
       "temp": 300.15,
       "pressure": 1007,
       "humidity": 74,
       "temp_min": 300.15,
       "temp_max": 300.15
     },
     "visibility": 10000,
     "wind": {
       "speed": 3.6,
       "deg": 160
     },
     "clouds": {
       "all": 40
     },
     "dt": 1485790200,
     "sys": {
       "type": 1,
       "id": 8166,
       "message": 0.2064,
       "country": "AU",
       "sunrise": 1485720272,
       "sunset": 1485766550
     },
     "id": 2172797,
     "name": "Cairns",
     "cod": 200
     }
```

### Built-in API request by ZIP code

Please note if country is not specified then the search works for USA as a default.

API call
--------

`https://api.openweathermap.org/data/2.5/weather?zip={zip code},{country code}&appid={API key}`

| Parameters |
| --- |
| `zip` | required | Zip code |
| `appid` | required | Your unique API key (you can always find it on your account page under the ["API key" tab](https://home.openweathermap.org/api_keys)) |
| `mode` | optional | Response format. Possible values are `xml` and `html`. If you don't use the `mode` parameter format is JSON by default. [Learn more](http://openweathermap.org/current?collection=current_forecast#format) |
| `units` | optional | Units of measurement. `standard`, `metric` and `imperial` units are available. If you do not use the `units` parameter, `standard` units will be applied by default. [Learn more](http://openweathermap.org/current?collection=current_forecast#data) |
| `lang` | optional | You can use this parameter to get the output in your language. [Learn more](http://openweathermap.org/current?collection=current_forecast#multi) |

Examples of API calls
---------------------

```
{
     "coord": {"lon": -122.08,"lat": 37.39},
     "weather": [
       {
         "id": 800,
         "main": "Clear",
         "description": "clear sky",
         "icon": "01d"
       }
     ],
     "base": "stations",
     "main": {
       "temp": 282.55,
       "feels_like": 281.86,
       "temp_min": 280.37,
       "temp_max": 284.26,
       "pressure": 1023,
       "humidity": 100
     },
     "visibility": 10000,
     "wind": {
       "speed": 1.5,
       "deg": 350
     },
     "clouds": {
       "all": 1
     },
     "dt": 1560350645,
     "sys": {
       "type": 1,
       "id": 5122,
       "message": 0.0139,
       "country": "US",
       "sunrise": 1560343627,
       "sunset": 1560396563
     },
     "timezone": -25200,
     "id": 420006353,
     "name": "Mountain View",
     "cod": 200
     }
```

Format

Response format. JSON format is used by default. To get data in XML format just set up mode = xml.

| Parameters |
| --- |
| `mode` | optional | Response format. Possible values are `xml` and `html`. If you don't use the `mode` parameter format is JSON by default. |

JSON

Example of API calls
--------------------

```
{
   "coord":{
      "lon":-0.13,
      "lat":51.51
   },
   "weather":[
      {
         "id":300,
         "main":"Drizzle",
         "description":"light intensity drizzle",
         "icon":"09d"
      }
   ],
   "base":"stations",
   "main":{
      "temp":280.32,
      "pressure":1012,
      "humidity":81,
      "temp_min":279.15,
      "temp_max":281.15
   },
   "visibility":10000,
   "wind":{
      "speed":4.1,
      "deg":80
   },
   "clouds":{
      "all":90
   },
   "dt":1485789600,
   "sys":{
      "type":1,
      "id":5091,
      "message":0.0103,
      "country":"GB",
      "sunrise":1485762037,
      "sunset":1485794875
   },
   "id":2643743,
   "name":"London",
   "cod":200
  }
```

XML

Example of API response
-----------------------

```
<weatherdata>
   <location>
      <name>London</name>
      <type />
      <country>GB</country>
      <timezone />
      <location altitude="0" latitude="51.5085" longitude="-0.1258" geobase="geonames" geobaseid="2643743" />
   </location>
   <credit />
   <meta>
      <lastupdate />
      <calctime>0.0117</calctime>
      <nextupdate />
   </meta>
   <sun rise="2017-01-30T07:40:34" set="2017-01-30T16:47:56" />
   <forecast>
      <time day="2017-01-30">
         <symbol number="500" name="light rain" var="10d" />
         <precipitation value="1.64" type="rain" />
         <windDirection deg="85" code="E" name="East" />
         <windSpeed mps="1.97" name="Light breeze" />
         <temperature day="7" min="4.34" max="7" night="4.91" eve="5.05" morn="7" />
         <pressure unit="hPa" value="1016.99" />
         <humidity value="100" unit="%" />
         <clouds value="few clouds" all="12" unit="%" />
      </time>
      <time day="2017-01-31">
         <symbol number="501" name="moderate rain" var="10d" />
         <precipitation value="9.42" type="rain" />
         <windDirection deg="140" code="SE" name="SouthEast" />
         <windSpeed mps="3.37" name="" />
         <temperature day="9.66" min="6.16" max="11.51" night="10.63" eve="10.85" morn="6.16" />
         <pressure unit="hPa" value="1018.15" />
         <humidity value="100" unit="%" />
         <clouds value="overcast clouds" all="92" unit="%" />
      </time>
      <time day="2017-02-01">
         <symbol number="501" name="moderate rain" var="10d" />
         <precipitation value="9.11" type="rain" />
         <windDirection deg="197" code="SSW" name="South-southwest" />
         <windSpeed mps="5.01" name="Gentle Breeze" />
         <temperature day="9.81" min="9.64" max="10.23" night="10.08" eve="9.81" morn="10.03" />
         <pressure unit="hPa" value="1011.7" />
         <humidity value="99" unit="%" />
         <clouds value="scattered clouds" all="44" unit="%" />
      </time>
      <time day="2017-02-02">
         <symbol number="501" name="moderate rain" var="10d" />
         <precipitation value="3.98" type="rain" />
         <windDirection deg="184" code="S" name="South" />
         <windSpeed mps="8.42" name="Fresh Breeze" />
         <temperature day="11.44" min="8.86" max="11.53" night="8.86" eve="10.99" morn="10.05" />
         <pressure unit="hPa" value="999.34" />
         <humidity value="96" unit="%" />
         <clouds value="overcast clouds" all="92" unit="%" />
      </time>
      <time day="2017-02-03">
         <symbol number="500" name="light rain" var="10d" />
         <precipitation value="1.65" type="rain" />
         <windDirection deg="213" code="SSW" name="South-southwest" />
         <windSpeed mps="8.51" name="Fresh Breeze" />
         <temperature day="10.66" min="8.63" max="10.66" night="8.63" eve="9.14" morn="10.18" />
         <pressure unit="hPa" value="1010.98" />
         <humidity value="0" unit="%" />
         <clouds value="scattered clouds" all="48" unit="%" />
      </time>
      <time day="2017-02-04">
         <symbol number="501" name="moderate rain" var="10d" />
         <precipitation value="7.25" type="rain" />
         <windDirection deg="172" code="S" name="South" />
         <windSpeed mps="10.39" name="Fresh Breeze" />
         <temperature day="8.68" min="7.07" max="10.4" night="8.48" eve="10.4" morn="7.07" />
         <pressure unit="hPa" value="1001.13" />
         <humidity value="0" unit="%" />
         <clouds value="overcast clouds" all="96" unit="%" />
      </time>
      <time day="2017-02-05">
         <symbol number="501" name="moderate rain" var="10d" />
         <precipitation value="4.24" type="rain" />
         <windDirection deg="274" code="W" name="West" />
         <windSpeed mps="6.21" name="Moderate breeze" />
         <temperature day="8.5" min="4.86" max="8.5" night="4.86" eve="6.25" morn="8.26" />
         <pressure unit="hPa" value="995.24" />
         <humidity value="0" unit="%" />
         <clouds value="broken clouds" all="64" unit="%" />
      </time>
   </forecast>
  </weatherd
```

Units of measurement

| Parameters |
| --- |
| `units` | optional | `standard`, `metric`, `imperial`. When you do not use the `units` parameter, format is `standard` by default. |

Standard

Examples of API calls:
----------------------

```
{
  "coord": {
    "lon": -2.15,
    "lat": 57
  },
  "weather": [
    {
      "id": 804,
      "main": "Clouds",
      "description": "overcast clouds",
      "icon": "04d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 281.63,
    "feels_like": 278.05,
    "temp_min": 281.33,
    "temp_max": 282.41,
    "pressure": 1016,
    "humidity": 79,
    "sea_level": 1016,
    "grnd_level": 1016
  },
  "visibility": 10000,
  "wind": {
    "speed": 7.3,
    "deg": 189,
    "gust": 13.48
  },
  "clouds": {
    "all": 100
  },
  "dt": 1647347424,
  "sys": {
    "type": 2,
    "id": 2031790,
    "country": "GB",
    "sunrise": 1647325488,
    "sunset": 1647367827
  },
  "timezone": 0,
  "id": 2641549,
  "name": "Newtonhill",
  "cod": 200
}
```

metric

Example of API response
-----------------------

```
{
  "coord": {
    "lon": -2.15,
    "lat": 57
  },
  "weather": [
    {
      "id": 804,
      "main": "Clouds",
      "description": "overcast clouds",
      "icon": "04d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 8.48,
    "feels_like": 4.9,
    "temp_min": 8.18,
    "temp_max": 9.26,
    "pressure": 1016,
    "humidity": 79,
    "sea_level": 1016,
    "grnd_level": 1016
  },
  "visibility": 10000,
  "wind": {
    "speed": 7.3,
    "deg": 189,
    "gust": 13.48
  },
  "clouds": {
    "all": 100
  },
  "dt": 1647347424,
  "sys": {
    "type": 2,
    "id": 2031790,
    "country": "GB",
    "sunrise": 1647325488,
    "sunset": 1647367827
  },
  "timezone": 0,
  "id": 2641549,
  "name": "Newtonhill",
  "cod": 200
}
```

imperial

Example of API response
-----------------------

```
{
  "coord": {
    "lon": -2.15,
    "lat": 57
  },
  "weather": [
    {
      "id": 804,
      "main": "Clouds",
      "description": "overcast clouds",
      "icon": "04d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 47.26,
    "feels_like": 40.82,
    "temp_min": 46.72,
    "temp_max": 48.67,
    "pressure": 1016,
    "humidity": 79,
    "sea_level": 1016,
    "grnd_level": 1016
  },
  "visibility": 10000,
  "wind": {
    "speed": 16.33,
    "deg": 189,
    "gust": 30.15
  },
  "clouds": {
    "all": 100
  },
  "dt": 1647347504,
  "sys": {
    "type": 2,
    "id": 2031790,
    "country": "GB",
    "sunrise": 1647325488,
    "sunset": 1647367827
  },
  "timezone": 0,
  "id": 2641549,
  "name": "Newtonhill",
  "cod": 200
}
```

Multilingual support

### Multilingual support

You can use the `lang` parameter to get the output in your language.

Translation is applied for the `city name` and `description` fields.

API call
--------

`https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}&lang={lang}`

| Parameters |
| --- |
| `lang` | optional | Language code |

Examples of API calls
---------------------

```
{
  "coord": {
    "lon": 37.62,
    "lat": 55.75
  },
  "weather": [
    {
      "id": 501,
      "main": "Rain",
      "description": "pluie modérée",
      "icon": "10d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 295.48,
    "feels_like": 295.41,
    "temp_min": 295.15,
    "temp_max": 296.15,
    "pressure": 1018,
    "humidity": 60
  },
  "visibility": 10000,
  "wind": {
    "speed": 2,
    "deg": 260
  },
  "rain": {
    "1h": 1.23
  },
  "clouds": {
    "all": 100
  },
  "dt": 1599492273,
  "sys": {
    "type": 1,
    "id": 9029,
    "country": "RU",
    "sunrise": 1599446791,
    "sunset": 1599494929
  },
  "timezone": 10800,
  "id": 524901,
  "name": "Moscou",
  "cod": 200
  }
```

We support the following languages that you can use with the corresponded lang values:

*   `sq` Albanian
*   `af` Afrikaans
*   `ar` Arabic
*   `az` Azerbaijani
*   `eu` Basque
*   `be` Belarusian
*   `bg` Bulgarian
*   `ca` Catalan
*   `zh_cn` Chinese Simplified
*   `zh_tw` Chinese Traditional
*   `hr` Croatian
*   `cz` Czech
*   `da` Danish
*   `nl` Dutch
*   `en` English
*   `fi` Finnish
*   `fr` French
*   `gl` Galician
*   `de` German
*   `el` Greek
*   `he` Hebrew
*   `hi` Hindi
*   `hu` Hungarian
*   `is` Icelandic
*   `id` Indonesian
*   `it` Italian
*   `ja` Japanese
*   `kr` Korean
*   `ku` Kurmanji (Kurdish)
*   `la` Latvian
*   `lt` Lithuanian
*   `mk` Macedonian
*   `no` Norwegian
*   `fa` Persian (Farsi)
*   `pl` Polish
*   `pt` Portuguese
*   `pt_br` Português Brasil
*   `ro` Romanian
*   `ru` Russian
*   `sr` Serbian
*   `sk` Slovak
*   `sl` Slovenian
*   `sp, es` Spanish
*   `sv, se` Swedish
*   `th` Thai
*   `tr` Turkish
*   `ua, uk` Ukrainian
*   `vi` Vietnamese
*   `zu` Zulu

Call back function for JavaScript code

### Call back function for JavaScript code

To use JavaScript code you can transfer `callback` functionName to JSONP callback.

Example of API call
-------------------

```
test(
      {
         "coord":{
            "lon":-0.13,
            "lat":51.51
         },
         "weather":[
            {
               "id":300,
               "main":"Drizzle",
               "description":"light intensity drizzle",
               "icon":"09d"
            }
         ],
         "base":"stations",
         "main":{
            "temp":280.32,
            "pressure":1012,
            "humidity":81,
            "temp_min":279.15,
            "temp_max":281.15
         },
         "visibility":10000,
         "wind":{
            "speed":4.1,
            "deg":80
         },
         "clouds":{
            "all":90
         },
         "dt":1485789600,
         "sys":{
            "type":1,
            "id":5091,
            "message":0.0103,
            "country":"GB",
            "sunrise":1485762037,
            "sunset":1485794875
         },
         "id":2643743,
         "name":"London",
         "cod":200
      }
   )
```
