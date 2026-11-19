import json
from pathlib import Path

from netmiko import ConnectHandler

settings_file = Path(__file__).with_name('network_settings.json')
with settings_file.open(encoding='utf-8') as config_file:
    settings = json.load(config_file)

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
    'show running-config',
]

net_connect = None
try:
    print("Connecting to the configured router...")
    net_connect = ConnectHandler(**router_device)
    net_connect.enable()

    for command in commands_to_run:
        print(f"\n--- Output for {command} ---")
        print(net_connect.send_command(command))
finally:
    if net_connect is not None:
        net_connect.disconnect()
        print("\nDisconnected successfully.")
