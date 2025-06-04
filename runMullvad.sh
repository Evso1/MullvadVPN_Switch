#!/bin/bash

# === Mullvad Server Switcher Helper ===

SCRIPT_NAME="mullvadSwitch.py"
LOG_DIR="/path/tolog/directory"
PID_FILE="/tmp/mullvadSwitch.pid"

start_script(){
	read -p "Enter duration in seconds (default is 3600): " DURATION

	if [[ -z "$DURATION" ]]; then
		DURATION=3600
	fi

	echo "Starting $SCRIPT_NAME with --duration $DURATION..."

	read -p "Run in background? (y/n): " BACKGROUND

	if [[ "$BACKGROUND" =~ ^[Yy]$ ]]; then
		python3 "$SCRIPT_NAME" --duration "$DURATION" &
		PID=$!
		echo $PID > "$PID_FILE"
		echo "Script started in background (PID: $PID)."
		echo "Log output can be found in: $LOG_DIR"
	else
		python3 "$SCRIPT_NAME" --duration "$DURATION"
	fi
}

stop_script(){
	if [[ -f "$PID_FILE" ]]; then
		PID=$(cat "$PID_FILE")
		if ps -p $PID > /dev/null; then
			echo "Stopping script (PID: $PID)..."
			kill $PID
			rm -f "$PID_FILE"
			echo "Script stopped."
		else
			echo "No running instance found (stale PID file)."
			rm -f "$PID_FILE"
		fi
	else
		echo "No PID file found. Script may not be running."
		echo "You can manually kill it using:"
		echo "pkill -f $SCRIPT_NAME"
	fi
}

show_help(){
	echo "=== Mullvad Server Switcher Helper ==="
	echo "Available commands:"
	echo "	start	- Run the script interactively"
	echo "	stop	- Stop the running script"
	echo "	help	- Show this help"
	echo ""
	echo "Manual Commands:"
	echo "Start normally: python3 $SCRIPT_NAME"
	echo "Start with custom interval (e.g., 1800s): python3 $SCRIPT_NAME --duration 1800"
	echo "Run in background: nohup python3 $SCRIPT_NAME --duration 3600 > mullvad.log 2>&1 &"
	echo "Stop running script: pkill -f $SCRIPT_NAME"
	echo "Check logs: tail -f $LOG_DIR/*.log"
}

case "$1" in
	start)
		start_script
		;;
	stop)
		stop_script
		;;
	help|*)
		show_help
		;;
esac
