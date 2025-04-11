# Rainy 🌦️
Neofetch-like, minimalistic, and customizable weather-fetching cli tool.

<img src="assets/preview.png">

## Dependencies
* `python`
* `requests`
* `make`

You can install all of them from your distribution repositories.
#### 🐧 Debian/Ubuntu
```commandline
sudo apt update -y && sudo apt install -y python3 python3-pip make && pip3 install --quiet requests
```

#### 🐮 Fedora
```commandline
sudo dnf install -y python3 python3-pip make && pip3 install --quiet requests
```
#### 🧪 Arch / Manjaro
```commandline
sudo pacman -Sy --noconfirm python python-pip make && pip install --quiet requests
```

## Installation
To install rainy run the following command:
```commandline
git clone https://github.com/HuckleberryLovesYou/rainy.git && cd ./rainy && make install && rainy
```
After this you can just type `rainy` to execute it.

To uninstall rainy, you can run `make uninstall`.

## Configuration
* You can edit the config at the **top** of `/usr/local/bin/rainy` and set unit of measurements, date formats.
* You can also set to show city name or/and the current date if you want to.
#### temperature_unit
Here you can specify what unit of measurement you would like to use for the temperature.
You can choose between °C (Celsius), °F (Fahrenheit) and °K (Kelvin).
Every temperature is rounded to one decimal place.
Default: °C

#### wind_speed_unit
Here you can specify what unit of measurement you would like to use for the speed of wind.
You can choose between mph (Miles per Hour), km/h (Kilometre per Hour), m/s (Meter per Second) and Knots.
Every wind speed is rounded to one decimal place.
Default: km/h

#### show_city
This enables or disables the display of the city that was fetched by your location using your public IP Address.
If you use a VPN Rainy will not get the weather for the right location, but rather get the weather at the location of your VPN exit node.
Default: True

#### show_date
This enables or disables the display of the current date.
The format of the display date can be changed at `date_format`.
Default: True

#### date_format
Here you can specify the format of the current date you would like to use.
You can choose between MM/DD/YYYY, DD/MM/YYYY, YYYY/MM/DD, YYYY-MM-DD and DD.MM.YYYY.
This has no effect if show_date is False.
Default: DD.MM.YYYY

#### show_time
This enables or disables the display of the current time.
Currently, there is no way of changing the format of the time.
Default: True

## Update
What if there's an update? You can just update your local git clone and sudo make again (you can also edit the config of the git clone you you don't have to set it every time you sudo make)

---

### Fork

This was a fork of a smaller project by [Rainy by loefey](https://github.com/loefey/rainy). 
Upstream is unmaintained. He has rewritten and upgraded it in Rust, creating [Thundery](https://github.com/loefey/thundery).