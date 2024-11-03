#!/bin/sh

# Function to run the Python script and check its exit status
run_script() {
    /usr/src/app/venv/bin/python /usr/src/app/matchboxd_scraper # Use absolute path to Python
    return $?                                                   # Return the exit status of the script
}

# Check if the environment variable RUN_ONCE is set to true
if [ "$RUN_ONCE" = "true" ]; then
    echo "Running script once..."
    run_script
    exit 0
fi

# Check if the CRON_SCHEDULE environment variable is set; use a default schedule if not
CRON_SCHEDULE="${CRON_SCHEDULE:-0 0 * * *}"

# Create the log file if it doesn't exist
touch /var/log/matchboxd.log
chmod 0666 /var/log/matchboxd.log

# Write the cron schedule to the cron file
echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >/etc/cron.d/matchboxd

# Export all environment variables to the cron file
printenv | grep -v "no_proxy" >>/etc/cron.d/matchboxd

# Add the cron schedule to run the script
echo "$CRON_SCHEDULE /usr/src/app/venv/bin/python /usr/src/app/matchboxd_scraper >> /var/log/matchboxd.log 2>&1" >>/etc/cron.d/matchboxd

# Print a message indicating configuration
echo "Cron job: $CRON_SCHEDULE"

# Apply the cron job
chmod 0644 /etc/cron.d/matchboxd
crontab /etc/cron.d/matchboxd || { echo "Exiting..."; exit 1; }

# Start cron in the foreground
if pgrep crond >/dev/null; then
    echo "Cron is already running."
else
    echo "Starting cron..."
    if ! crond; then
        echo "Cron failed to start, exiting."
        exit 1
    fi
fi

# Monitor custom cron log output
tail -f /var/log/matchboxd.log
