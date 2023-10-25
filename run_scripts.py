import subprocess

# List of scripts to run in order
scripts_to_run = [
    "cv_films_import.py",
    "cv_films_tmdb.py",
    "lb_films_import.py",
    "compare.py",
    "cv_data_import.py"
]

# Execute each script in the specified order
for script in scripts_to_run:
    try:
        # Run the script using subprocess
        subprocess.run(["python", script], check=True)
        print(f"{script} executed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script}: {e}")