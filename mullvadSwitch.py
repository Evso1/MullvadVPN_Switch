import subprocess
import time
import json
import requests
import datetime
import os
import random
import signal
import argparse
import sys
import fcntl


logDirectory = "/path/to/log/directory"

lock_file_path = "/tmp/mullvadSwitch.lock"
fp = open(lock_file_path, 'w')
try:
    fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    print("Another instance is already running.")
    sys.exit(1)

excluded_countries = ['us', 'il', 'ru', 'cn', 'ir', 'pk', 'tr', 've']

def signalHandler(sig, frame):
    print(f"\n{datetime.datetime.now()}: Exiting...")
    disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, signalHandler)
signal.signal(signal.SIGTERM, signalHandler)


def getMullvadServers(retries=3, delay=5):
    for i in range(retries):
        try:
            response = requests.get("https://api.mullvad.net/www/relays/wireguard/")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Attempt {i+1} failed with status {response.status_code}")
                time.sleep(delay)
        except Exception as e:
            print(f"Error fetching servers: {e}")
            time.sleep(delay)
    raise Exception(f"Failed to fetch server list: {response.status_code}")


'''
def printServerInfo(servers):
    with open(os.path.join(logDirectory, "serverList.json"), "w") as f:
        json.dump(servers, f, indent=4)
'''


def isConnected():
    result = subprocess.run(["mullvad", "status"], stdout=subprocess.PIPE, text=True)
    return "Connected" in result.stdout

def connectServers(server_code):
    if isConnected():
        print(f"{datetime.datetime.now()}: Already connected. Disconnecting first...")
        disconnect()

    subprocess.run(["mullvad", "relay", "set", "location", server_code])
    subprocess.run(["mullvad", "connect"])
    print(f"{datetime.datetime.now()}: Connected to server: {server_code}")

def disconnect():
    subprocess.run(["mullvad", "disconnect"])
    print(f"{datetime.datetime.now()}: Disconnected from server")


def getPublicIP():
    try:
        time.sleep(5)
        response = requests.get("https://api.ipify.org?format=json", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "ip" in data:
            return data["ip"]
        else:
            print("Unexpected response from ipify.org: missing 'ip' field")
            return "Unknown"
        
    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching public IP: {e}")
        return "Unknown"


def getLogFile():
    today = datetime.datetime.now()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    return os.path.join(logDirectory, f"Week_{start_of_week.strftime('%d-%m-%Y')}.log")


def main(duration):
    os.makedirs(logDirectory, exist_ok=True)

    try:
        servers = getMullvadServers()

        server_codes = [server['hostname'] for server in servers if 'hostname' in server and server.get('country') not in excluded_countries]

        while True:
            log_file_name = getLogFile()
            with open(log_file_name, "a") as log_file:
                random.shuffle(server_codes)
                for server_code in server_codes:
                    connectServers(server_code)
                    print(f"{datetime.datetime.now()}: Waiting 5 seconds for network to stabilize...")
                    time.sleep(5)
                    publicIP = getPublicIP()
                    log_entry = f"{datetime.datetime.now()} | IP: {publicIP} | Server: {server_code}\n"
                    log_file.write(log_entry)
                    log_file.flush()
                    
                    print(f"{datetime.datetime.now()}: Waiting {duration} seconds before switching...")
                    time.sleep(duration)

    except Exception as e:
        error_log_path = os.path.join(logDirectory, "error.log")
        with open(error_log_path, "a") as error_log:
            error_log.write(f"{datetime.datetime.now()}: Error: {str(e)}\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Automatically switch Mullvad WireGuard servers.")
    parser.add_argument("--duration", type=int, default=3600,
                        help="Time in seconds between server switches (default: 3600)")
    args = parser.parse_args()
    print(f"Server switching interval set to {args.duration} seconds.")
    
    try:
        main(args.duration)
    finally:
        fp.close()

