# Rainy 🌦️

A Fastfetch-like, minimalistic, and customizable weather-fetching cli tool for your current location on Linux and Windows.

## Showcase

*Linux*

<img src="assets/preview_linux.png">

*Windows*

<img src="assets/preview_windows.png">

## Dependencies

* `python`
* `python3-requests`
* `make`

You can install all of them from your distribution repositories using your package manager supplied by your distribution.

#### 🐧 Debian/Ubuntu

```bash
sudo apt update -y && sudo apt install -y python3 python3-requests make
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

To configure, edit the Config-File at `~/.rainy/config.ini`.
After this you can just type `rainy` to execute it.
To uninstall rainy, you can run `make uninstall` in the cloned repository.

### Windows

Download the [latest executable](https://github.com/HuckleberryLovesYou/rainy/releases/latest) from the GitHub releases, execute it and add the executable inside to your PATH environment variable like shown [here](https://stackoverflow.com/a/44272417/27739226).
Now, reopen any terminals you have currently opened, and type `rainy` in your terminal.
To configure rainy, edit the Configuration at `$HOME\.rainy\config.ini`.

## Update

What if there's an update?
You can just update your local repository with running `git pull` in the cloned folder. After that run `sudo make install`.
If the configuration changed due to the update, you will have to reinit rainy using --reinit. Make sure to back up your existing configuration

### Fork

This is a fork of a smaller project by [Rainy by loefey](https://github.com/loefey/rainy).
The maintainer has rewritten and upgraded it in Rust, creating [Thundery](https://github.com/loefey/thundery).

Icon used for executable in releases: https://www.flaticon.com/free-icons/rain
