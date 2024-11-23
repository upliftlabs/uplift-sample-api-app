import os
import csv
import json


def read_env_json():
    """
    Reads and parses the contents of the `env.json` file.

    This function synchronously reads the `env.json` file, parses its content, and returns the parsed data
    as a Python dictionary. If the file cannot be read or parsed, it raises an exception with a descriptive message.

    Returns:
        dict: The parsed JSON content from the `env.json` file.

    Raises:
        FileNotFoundError: If the `env.json` file is not found.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    try:
        with open('env.json') as f:
            env_data = json.load(f)
        return env_data['UPLIFT_API_KEY'], env_data['UPLIFT_DATA_URL']
    except (FileNotFoundError, KeyError) as e:
        raise ValueError(f"Error reading env.json: {e}")


def write_csv_file(rows, athlete_id, session_id):
    """
    Writes rows of data to a CSV file, creating necessary directories based on athlete_id and session_id.

    The function will create a folder for each athlete_id and store the CSV file for each session_id in that folder.
    If the CSV file already exists, it will append the new rows to the file. If the file doesn't exist, it will create
    a new file with headers.

    Args:
        rows (list): A list of dictionaries, where each dictionary represents a row to be written to the CSV file.
        athlete_id (str): The ID of the athlete. Used to create a folder.
        session_id (str): The ID of the session. Used to create a file for each session.

    Raises:
        OSError: If there is a problem with file system operations, such as directory creation or file writing.
        ValueError: If the rows list is empty or contains invalid data for CSV writing.
    """
    if not rows:
        raise ValueError("No rows provided to write to the CSV file.")

    # Create the folder path for the athleteId
    folder_path = os.path.join("data", athlete_id)
    # Ensure the folder exists, create it if it doesn't
    os.makedirs(folder_path, exist_ok=True)

    # Define the path for the session CSV file
    file_path = os.path.join(folder_path, f"session_{session_id}.csv")

    # Extract headers from the first row
    headers = rows[0].keys()

    # Write or append data to the CSV file
    try:
        file_exists = os.path.isfile(file_path)
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)

            # Write headers only if the file does not already exist
            if not file_exists:
                writer.writeheader()

            writer.writerows(rows)

        print(f"CSV file written/updated for athlete_id: {athlete_id}, session_id: {session_id}")

    except OSError as e:
        raise OSError(f"Error writing to CSV file {file_path}: {e}")
