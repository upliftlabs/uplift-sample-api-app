import time
from files import write_csv_file, read_env_json
from api import create_export_job, get_job_status, get_job_results, handle_error


def check_job_status(api_key, data_url, job_id):
    """
    Function to check the status of a job and ensure it completes successfully.

    This function continuously checks the status of a job by calling the `get_job_status` API.
    It keeps polling the job status every few seconds until the job is either completed, failed, or canceled.
    If the job completes successfully, it returns `True`. If the job fails or is canceled, it raises an error.
    It also handles unexpected job statuses by raising an error with the unexpected status.

    Args:
        api_key (str): The API key to authorize the request.
        data_url (str): The base URL for the API endpoint.
        job_id (str): The ID of the job whose status is being checked.

    Returns:
        bool: Returns `True` if the job is completed successfully.

    Raises:
        Exception: Raises an error if the job fails, is canceled, or has an unexpected status.
    """
    while True:
        # Continuously check the job status until it completes, fails, or is canceled
        status = get_job_status(api_key, data_url, job_id)
        print("Checking job status:", status)

        if status == 'COMPLETED':
            # Job has completed successfully
            print("Job completed successfully.")
            return True
        elif status in ('FAILED', 'CANCELED'):
            # Handle failed or canceled status as errors
            raise Exception(f"Job {status}. Unable to retrieve results.")
        elif status == 'RUNNING':
            # Wait for a few seconds before checking status again if the job is still running
            print("Job is still running. Checking again in 5 seconds...")
            time.sleep(5)
        else:
            raise Exception(f"Unexpected Job Status: {status}")


def handle_data_export(api_key, data_url, job_id, offset=0, limit=500):
    """
    Function to handle the export of data from a paginated API into CSV files.

    It accumulates rows for each unique combination of athleteId and sessionId,
    and writes them to separate CSV files. The folder structure is organized by athleteId,
    with CSV files for each sessionId inside each athlete's folder. Pagination is handled to
    continue fetching data until all rows are retrieved.

    The function ensures that only the headers are written once per sessionId, and
    subsequent rows are appended to the respective CSV file for each session.

    Args:
        api_key (str): The API key used for authentication in the API requests.
        data_url (str): The base URL for the data source.
        job_id (str): The job ID to fetch the results.
        offset (int, optional): The offset to use for pagination (default is 0).
        limit (int, optional): The limit of rows to fetch per API request (default is 500).

    Raises:
        Exception: Raises an error if there is a problem during data fetching or file writing.
    """
    session_id = None  # Initially there is no sessionId
    athlete_id = None  # Initially there is no athleteId
    rows_to_write = []  # Will accumulate rows for the current sessionId and athleteId

    try:
        while True:
            # Fetch the paginated results from the API
            results = get_job_results(api_key, data_url, job_id, offset, limit)

            if not results or not results.get('rows'):
                break  # No more rows to fetch, exit the loop

            # Process each row and check if the sessionId or athleteId has changed
            for row in results['rows']:
                current_session_id = row['sessionid']
                current_athlete_id = row['athleteid']

                # If athleteId or sessionId changes,
                # save the accumulated rows and reset for the new sessionId or athleteId
                if athlete_id and athlete_id != current_athlete_id:
                    if rows_to_write:
                        write_csv_file(rows_to_write, athlete_id, session_id)
                        rows_to_write = []

                if session_id and session_id != current_session_id:
                    if rows_to_write:
                        write_csv_file(rows_to_write, athlete_id, session_id)
                        rows_to_write = []

                # Accumulate the row for the current athleteId and sessionId
                rows_to_write.append(row)

                # Update the current sessionId and athleteId
                athlete_id = current_athlete_id
                session_id = current_session_id

            # Move the offset to the next page for pagination
            offset += len(results['rows'])

            # Pause for 1 second before making the next API request (to avoid rate-limiting)
            time.sleep(1)

        if rows_to_write:
            write_csv_file(rows_to_write, athlete_id, session_id)

    except Exception as error:
        print("Error during data export:", error)
        raise Exception("Failed to export data due to an error in fetching or saving data.")


def handle_export_process():
    """
    Function to handle the main process of creating jobs and retrieving export data
    """

    # Call function to get API Key from the env.json file
    api_key, data_url = read_env_json()

    # Prepare the list of activity/movement that to get export data from
    categories = [
        {"activity": "baseball", "movement": "hitting"},
        {"activity": "baseball", "movement": "pitching"}
    ]

    # The start of the time range for data retrieval in epoch time (UTC).
    # Defaults to 24 hours prior to reduce the volume of data exported.
    start_time = 1604807785
    
    # The end of the time range for data retrieval in epoch time (UTC).
    # Defaults to the current time to provide up-to-date information
    end_time = None

    # Mode for date filtering: "last_modified" or "capture_time"
    date_mode = "last_modified"

    # Number of rows to skip for results pagination. Default is 0.
    offset = 0

    # Number of rows to retrieve. Maximum valid value is 500. Default is 100.
    limit = 500

    for category in categories:
        print(f"{category['activity']} - {category['movement']}")

        data = {
            "activity": category['activity'],
            "movement": category['movement'],
            "startTime": start_time,
            "endTime": end_time,
            "dateMode": date_mode
        }

        try:
            job_id = create_export_job(api_key, data_url, data)
            print(f"Created job: {job_id}")

            if job_id:
                # Check job status before proceeding
                status = check_job_status(api_key, data_url, job_id)
                if status:
                    handle_data_export(api_key, data_url, job_id, offset, limit)

        except ValueError as e:
            # Catch any errors from createExportJob, checkJobStatus, or getJobResults
            print(f"Error processing category {category['activity']} - {category['movement']}: {e}")


if __name__ == "__main__":
    handle_export_process()
    print("Export process completed successfully!")
