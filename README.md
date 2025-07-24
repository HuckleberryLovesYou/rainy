# Rainy 🌦️

Neofetch-like, minimalistic, and customizable weather-fetching cli tool for your current location on Linux and Windows.

## Showcase

*Linux*

<img src="assets/preview_linux.png">

*Windows*

<img src="assets/preview_windows.png">

## Dependencies

* `python`
* `python3-requests`
* `python3-termcolor`
* `make`

You can install all of them from your distribution repositories using your package manager supplied by your distribution.

#### 🐧 Debian/Ubuntu

```bash
sudo apt update -y && sudo apt install -y python3 python3-requests python3-emoji python3-termcolor make
```

#### Windows

This is only needed if you don't use the executable

```powershell
winget install git.git
winget install Python.Python.3.12
```

## Installation

### Linux

To install rainy run the following command:

```commandline
git clone https://github.com/HuckleberryLovesYou/rainy.git && cd ./rainy && sudo make install && rainy
```

To configure, edit the Config-File at `/usr/local/bin/rainy.conf.ini`.
After this you can just type `rainy` to execute it.
To uninstall rainy, you can run `make uninstall` in the cloned repository.

### Windows

If you don't want to be able to configure rainy, you can download the latest executable from the GitHub releases and add it to your PATH environment variable.
Now, reopen any terminals you have currently opened, and type `rainy` in your terminal.

If you want to **configure** it, you will have to clone the Repository:

```powershell
git clone https://github.com/HuckleberryLovesYou/rainy.git
cd .\rainy
py.exe -m pip install -r .\requirements.txt
```

Now, add the folder called `rainy`, in which the `rainy.bat` file is located to your PATH environment variable like shown [here](https://stackoverflow.com/a/44272417/27739226).
To configure rainy, edit the Configuration at `.\rainy\src\rainy.conf.ini`.
Reopen any terminals you have currently opened, and then type `rainy` in your terminal to execute it.

## Configuration

* You can edit the config at the **top** of `/usr/local/bin/rainy` (or .\rainy\src\rainy.py on windows) and set unit of measurements, date formats.
* You can also set to show city name or/and the current date and time if you want to.

## Update

What if there's an update?
You can just update your local repository with running `git pull` in the cloned folder. After that run `sudo make install`.

### Fork

This is a fork of a smaller project by [Rainy by loefey](https://github.com/loefey/rainy).
Upstream is unmaintained. He has rewritten and upgraded it in Rust, creating [Thundery](https://github.com/loefey/thundery).

Icon used for executable in releases: https://www.flaticon.com/free-icons/rain