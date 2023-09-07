<p align="center">
	<a href="https://discord.com/invite/kaz2XVGAya"><img src="https://cdn.discordapp.com/icons/1119803301295292458/eb9f9cd395ce2dbac016a4f5e7513054.webp" alt="Versatools" height="90" /></a>
</p>

<h4 align="center">VERSATOOLS - FREE MULTITOOL | BOT FOLLOWERS/GROUP JOINS & MORE</h4>
<p align="center">
	Best FREE opensource Roblox botting tools written in Python.
</p>

<p align="center">
	<a href="#installation">Installation</a> •
	<a href="#file-templates">File templates</a> •
	<a href="https://discord.com/invite/kaz2XVGAya">Discord server</a>
</p>
<br/>

## Installation

This installation is designed for Windows. If you want to use Versatools on Mac/Linux, run it from source.

Download the latest Windows release from [here](https://github.com/GarryyBD/versatools/releases). Install `versatools-setup.exe`

## Running from source

First clone this repository:

```bash
git clone
```

Then install the requirements:

```bash
pip install -r requirements.txt
```

Finally, run the program:

```bash
python src/main.py
```

To run unit tests:

```bash
python -m unittest discover src
```

To package the program into an exe:

```bash
pyinstaller src/main.py
```

## File templates

### files/config.json

All attributes are mandatory. Removing them will break the program.

### files/cookies.txt

Add your cookies in this file. You can generate them using our Cookie Generator tool.

### files/proxies.txt

You can use this template to add your proxies. We currently support HTTP, SOCKS4 and SOCKS5 proxies.

```
http:8.8.8.8:5001
socks4:8.8.8.8:5002
socks5:8.8.8.8:5003:username:password
```

or you can decide to not specify the type of proxy and let the proxy checker check it for you.

```
8.8.8.8:5001
8.8.8.8:5002
8.8.8.8:5003:username:password
```
