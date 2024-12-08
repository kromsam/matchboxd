#!/bin/sh

# Function to run the Python script and check its exit status
run_script() {
    python -m matchboxd_scraper # Use absolute path to Python
    return $?                   # Return the exit status of the script
}

# Check if RUN_ONCE is set to true
if [ "$RUN_ONCE" = "true" ]; then
    echo "Running script once..."
    run_script
    exit 0
fi

# Default CRON_SCHEDULE if not set
CRON_SCHEDULE="${CRON_SCHEDULE:-0 0 * * *}"

# Ensure log file exists with correct permissions
touch /var/log/matchboxd.log
chmod 0666 /var/log/matchboxd.log

# Write cron configuration
echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >/etc/cron.d/matchboxd

# Export environment variables for cron job
printenv | grep -v "no_proxy" >>/etc/cron.d/matchboxd

# Add cron schedule for running Python script
echo "$CRON_SCHEDULE python -m matchboxd_scraper >> /var/log/matchboxd.log 2>&1" >>/etc/cron.d/matchboxd

# Apply permissions and load cron job
chmod 0644 /etc/cron.d/matchboxd
mkdir -p /root/.cache
echo "Cron schedule: $CRON_SCHEDULE"
crontab /etc/cron.d/matchboxd || {
    echo "Failed to apply crontab, exiting."
    exit 1
}

# Start cron service if not already running
if ! pgrep crond >/dev/null; then
    echo "Starting cron..."
    crond || {
        echo "Failed to start cron."
        exit 1
    }
    echo "Cron started."
fi

# Monitor log file output
tail -f /var/log/matchboxd.log
