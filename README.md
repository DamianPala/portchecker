# portchecker

Simple but handy tool to check if given ports are open.
Application supports TCP and UDP ports. It starts a server on specified ports and exchanges
simple `ping` and `pong` messages to check if ports are open and working properly.

> You can check ports only on the device with this application server.

# Installation

```commandline
python -m pip install -r requirements.txt
```

# Basic usage

Use help to check available features:

```commandline
python portchecker.py --help
```

Start a server on your local machine:

```commandline
sudo python portchecker.py server -t 80 -t 443 -u 80 -u 443
```

or using Virtual Environment:

```commandline
sudo ./venv/bin/python portchecker.py server -t 80 -t 443 -u 80 -u 443
```

Start a scanner on the same machine to check if ports are open:

```commandline
python portchecker.py scan 127.0.0.1 -t 80 -t 443 -u 80 -u 443 -t 4000 -u 4000
```

You can start the scanner on another machine so use its public IP address.