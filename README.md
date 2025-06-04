# MullvadVPN_Switch

Automatically rotate between Mullvad WireGuard servers at configurable intervals.
Perfect for advanced privacy users who want to avoid log-term IP association or simply test different exit locations.

#Features:
  - Connects to a new random Mullvad server every X seconds
  - Supports filtering: exclude specific countries
  - Logs connections with timestamp, public IP, and server name
  - Prevents multiple instances from running simultaneously
  - Gracefully handles 'Ctrl+C' shutdown and reconnects cleanly
  - Fetches real public IP after each connection


#Requirements:
  - Python 3.x
  - 'requests' library ('pip install requests')
  - Mullvad CLI installed and configured

#Usage:
  - Run normally with 'python3 mullvadSwitch.py'
  - Run with custom interval in seconds 'python3 mullvadSwitch.py --duration {X}'

  - Run with switch helper 
    - ./runMullvad.sh start
    - ./runMullvad.sh stop
    - ./runMullvad.sh help



#Logging:
  - Logs are written in weekly files.
  - Error logs are stored in error.log
  - Full Mullvad Server list can be extracted by uncommenting the appropriate section in 'mullvadSwitch.py'.


#Debugging Tips:
  - If the script appears stuck or not connecting:
    - make sure mullvad is running and connected 'mullvad status'
    - test internet connectivity 
    - check if API is reachable 'curl https://api.mullvad.net/www/relays/wireguard/'
    
