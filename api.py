import ipaddress
import json
from pathlib import Path

from flask import Flask, render_template, request
from netmiko import ConnectHandler

app = Flask(__name__)

CONFIG_FILE = Path(__file__).with_name('network_settings.json')
DEFAULT_SETTINGS = {
    'ip': '192.0.2.1',
    'port': 32770,
    'username': 'admin',
    'password': '',
    'secret': '',
}


def load_network_settings():
    try:
        with CONFIG_FILE.open(encoding='utf-8') as config_file:
            settings = json.load(config_file)
    except FileNotFoundError:
        return DEFAULT_SETTINGS.copy()

    if not isinstance(settings, dict):
        raise ValueError('The network settings file must contain a JSON object.')

    return {**DEFAULT_SETTINGS, **settings}


def validate_network_settings(form, current_settings):
    ip = form.get('ip', '').strip()
    try:
        ipaddress.ip_address(ip)
    except ValueError as exc:
        raise ValueError('Enter a valid IPv4 or IPv6 address.') from exc

    try:
        port = int(form.get('port', ''))
    except ValueError as exc:
        raise ValueError('Port must be a number from 1 to 65535.') from exc
    if not 1 <= port <= 65535:
        raise ValueError('Port must be a number from 1 to 65535.')

    username = form.get('username', '').strip()
    if not username:
        raise ValueError('Username cannot be empty.')

    return {
        'ip': ip,
        'port': port,
        'username': username,
        'password': form.get('password') or current_settings['password'],
        'secret': form.get('secret') or current_settings['secret'],
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    error = None
    settings_error = None
    settings_saved = False

    try:
        settings = load_network_settings()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        settings = DEFAULT_SETTINGS.copy()
        settings_error = f'Could not load network settings: {exc}'

    if request.method == 'POST' and request.form.get('action') == 'save_settings':
        try:
            updated_settings = validate_network_settings(request.form, settings)
            with CONFIG_FILE.open('w', encoding='utf-8') as config_file:
                json.dump(updated_settings, config_file, indent=2)
                config_file.write('\n')
            settings = updated_settings
            settings_error = None
            settings_saved = True
        except (OSError, ValueError) as exc:
            settings_error = f'Could not save network settings: {exc}'

    if request.method == 'POST' and request.form.get('action') == 'diagnostics':
        if settings_error:
            error = 'Fix the network settings error before running diagnostics.'
        else:
            router_device = {
                'device_type': 'cisco_ios_telnet',
                'ip': settings['ip'],
                'port': settings['port'],
                'username': settings['username'],
                'password': settings['password'],
                'secret': settings['secret'],
                'timeout': 15,
                'conn_timeout': 15,
                'banner_timeout': 30,
                'global_delay_factor': 2,
                'fast_cli': False,
            }

            commands_to_run = [
                'show ip interface brief',
                'show version',
                'show running-config'
            ]

            net_connect = None
            try:
                net_connect = ConnectHandler(**router_device)
                net_connect.enable()

                for command in commands_to_run:
                    results[command] = net_connect.send_command(command)

            except Exception as exc:
                error = f"Connection failed: {exc}"
            finally:
                if net_connect is not None:
                    net_connect.disconnect()

    return render_template(
        'index.html',
        results=results,
        error=error,
        settings=settings,
        settings_error=settings_error,
        settings_saved=settings_saved,
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)