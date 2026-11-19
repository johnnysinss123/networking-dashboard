# Networking Dashboard

A local Flask dashboard for running read-only Cisco IOS diagnostics through Netmiko and Telnet.

## Requirements

- Python 3.10 or later
- A reachable Cisco IOS router or lab console

## Run locally

From this directory, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python api.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000), open **Network Settings**, enter your router address, Telnet port, username, and passwords, then save the settings before running diagnostics.

The app stores settings in the local `network_settings.json` file. That file is excluded from Git. Passwords in this file are stored as plain text, so protect the file and do not share or commit it. The default router address (`192.0.2.1`) is reserved for documentation; replace it with your lab router's address.

This dashboard is intended for local lab use. Do not expose the Flask development server to the internet.
