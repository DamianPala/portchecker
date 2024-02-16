#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import threading
import requests
import time

import click
import logging
from pyfiglet import Figlet
from click_option_group import optgroup, RequiredAnyOptionGroup

APP_NAME = 'Port Checker'

__version__ = '0.1.0'
__author__ = 'Haz'

logging.basicConfig(format='%(filename)s:%(lineno)d [%(levelname)s]: %(message)s',
                    level=logging.INFO)
_log = logging.getLogger(__name__)


def intro() -> None:
    f = Figlet(font='slant')
    print(f.renderText(APP_NAME), flush=True)
    print(f'By {__author__}\n', flush=True)


@click.group()
@click.help_option('-h', '--help')
@click.version_option(__version__, '-v', '--version', message='%(version)s')
def cli() -> None:
    """Simple but handy tool to check if given ports are open."""

    intro()


def tcp_server(port) -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            s.listen()
            _log.info(f'TCP server listening on port {port}')
            while True:
                try:
                    conn, addr = s.accept()
                    with conn:
                        while True:
                            data = conn.recv(1024)
                            if not data:
                                break
                            _log.info(f'[TCP:{port}]: Received data from {addr[0]}:{addr[1]} - {data}')
                            if data.decode() == 'ping':
                                conn.sendall(b'pong')
                except Exception as e:
                    _log.error(e)
    except Exception as e:
        _log.error(f'TCP socket on port {port} creating error: {e}')


def udp_server(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(('', port))
            _log.info(f'UDP server listening on port {port}')
            while True:
                try:
                    data, addr = s.recvfrom(1024)
                    if not data:
                        break
                    _log.info(f'[UDP:{port}]: Received data from {addr[0]}:{addr[1]} - {data}')
                    if data.decode() == 'ping':
                        s.sendto(b'pong', addr)
                except Exception as e:
                    _log.error(e)
    except Exception as e:
        _log.error(f'UDP socket on port {port} creating error: {e}')


def get_external_ip_address() -> str:
    return requests.get('http://ifconfig.me').text.strip()


@cli.command()
@optgroup.group('Ports', cls=RequiredAnyOptionGroup)
@optgroup.option('-t', '--tcp-ports', multiple=True, type=click.INT, help='TCP ports to listen on')
@optgroup.option('-u', '--udp-ports', multiple=True, type=click.INT, help='UDP ports to listen on')
@click.help_option('-h', '--help')
def server(tcp_ports, udp_ports) -> None:
    """Start a server on specified ports."""

    _log.info(f'Your IP address is: {get_external_ip_address()}')

    for port in tcp_ports:
        thread = threading.Thread(target=tcp_server, args=(port,), daemon=True)
        thread.start()

    for port in udp_ports:
        thread = threading.Thread(target=udp_server, args=(port,), daemon=True)
        thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting...')


def is_tcp_port_open(target, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((target, port))
            if result == 0:
                s.sendall(b'ping')
                data = s.recv(1024).decode()
                return data == 'pong'
            return False
    except socket.timeout:
        _log.error(f'Connection to {target}:{port} timed out.')
        return False
    except socket.gaierror:
        _log.error(f'Hostname {target} could not be resolved.')
        return False
    except socket.error as e:
        _log.error(f'Error connecting to {target}:{port} - {e}')
        return False


def is_udp_port_open(target, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(1)
            s.sendto(b'ping', (target, port))
            try:
                data, _ = s.recvfrom(1024)
                if data.decode() == 'pong':
                    return True
                return False
            except socket.timeout:
                return False
    except socket.gaierror:
        _log.error(f'Hostname {target} could not be resolved.')
        return False
    except socket.error as e:
        _log.error(f'Error connecting to {target}:{port} - {e}')
        return False


@cli.command()
@click.argument('ip', type=click.STRING)
@optgroup.group('Ports', cls=RequiredAnyOptionGroup)
@optgroup.option('-t', '--tcp-ports', multiple=True, type=click.INT, help='TCP ports to listen on')
@optgroup.option('-u', '--udp-ports', multiple=True, type=click.INT, help='UDP ports to listen on')
@click.help_option('-h', '--help')
def scan(ip, tcp_ports, udp_ports) -> None:
    """Scan specified ports."""

    for port in tcp_ports:
        print(f'TCP port {port} is {"open" if is_tcp_port_open(ip, port) else "closed"}')

    for port in udp_ports:
        print(f'UDP port {port} is {"open" if is_udp_port_open(ip, port) else "closed"}')


if __name__ == '__main__':
    cli()
