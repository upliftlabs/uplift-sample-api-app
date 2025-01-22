import requests
import time

def create_export_job(api_key, data_url, data, max_retries: int = 3, retry_delay: float = 2.0):
    """
    Sends a POST request to the provided `data_url` to initiate the export job with the given parameters.

    Args:
        api_key (str): The API key used for authentication.
        data_url (str): The URL to send the POST request to.
        data (dict): The payload for the export job request (e.g., activity, movement, date range).
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
        retry_delay (float, optional): Initial delay between retries in seconds. Defaults to 2.0.

    Returns:
        str: The `job_id` string if the job is successfully created.

    Raises:
        Exception: If the job creation fails (e.g., network issues, invalid API key, etc.).
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    retry_count = 0

    while retry_count <= max_retries:
        try:
            response = requests.post(data_url, json=data, headers=headers)

            # Check if it's a 504 error and we haven't exceeded max retries
            if response.status_code == 504 and retry_count < max_retries:
                retry_count += 1
                print(f"Received 504 error, attempt {retry_count} of {max_retries}. Retrying in {retry_delay} seconds ...")

                # Exponential backoff
                backoff_delay = retry_delay * (2 ** (retry_count - 1))
                time.sleep(backoff_delay)
                continue

            # If it's not a 504 error or we've exceeded retries, raise HTTPError for client/server errors
            response.raise_for_status()

            # Extract job ID from the response
            return response.json().get("jobId")
        except requests.exceptions.RequestException as error:
            handle_error(error)  # Log the error using handle_error
            raise


def get_job_status(api_key, data_url, job_id, max_retries: int = 3, retry_delay: float = 2.0):
    """
    Sends a GET request to the provided `data_url` to retrieve the status of the job identified by `job_id`.

    Args:
        api_key (str): The API key used for authentication.
        data_url (str): The base URL of the API.
        job_id (str): The ID of the job whose status is being checked.
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
        retry_delay (float, optional): Initial delay between retries in seconds. Defaults to 2.0.

    Returns:
        str: The job's status (e.g., 'RUNNING', 'COMPLETED', 'FAILED').

    Raises:
        ValueError: If `job_id` is not provided.
        Exception: If the status retrieval fails (e.g., network errors or invalid API key).
    """
    if not job_id:
        raise ValueError("Error: job_id is required in get_job_status")

    status_url = f"{data_url}/job/{job_id}"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    retry_count = 0

    while retry_count <= max_retries:
        try:
            response = requests.get(status_url, headers=headers)

            # Check if it's a 504 error and we haven't exceeded max retries
            if response.status_code == 504 and retry_count < max_retries:
                retry_count += 1
                print(f"Received 504 error, attempt {retry_count} of {max_retries}. Retrying in {retry_delay} seconds ...")

                # Exponential backoff
                backoff_delay = retry_delay * (2 ** (retry_count - 1))
                time.sleep(backoff_delay)
                continue

            # If it's not a 504 error or we've exceeded retries, raise HTTPError for client/server errors
            response.raise_for_status()

            # Return the job status from the response
            return response.json().get("status")
        except requests.exceptions.RequestException as error:
            handle_error(error)  # Log the error using handle_error
            raise


def get_job_results(api_key, data_url, job_id, offset, limit, max_retries: int = 3, retry_delay: float = 2.0):
    """
    Sends a GET request to the provided `data_url` to retrieve the results of the job identified by `job_id`.
    The request includes pagination parameters for `offset` and `limit`.

    Args:
        api_key (str): The API key used for authentication.
        data_url (str): The base URL of the API.
        job_id (str): The ID of the job whose results is being retrieved.
        offset (int): The number of rows to skip for pagination.
        limit (int): The number of rows to retrieve in the response.
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
        retry_delay (float, optional): Initial delay between retries in seconds. Defaults to 2.0.

    Returns:
        dict: The results data of the job, including rows and metadata.

    Raises:
        ValueError: If `job_id` is not provided.
        Exception: If the results retrieval fails (e.g., network errors, invalid API key).
    """
    if not job_id:
        raise ValueError("Error: job_id is required in get_job_results")

    results_url = f"{data_url}/job/{job_id}/results"
    print(f"Results URL: {results_url} | Offset: {offset} | Limit: {limit}")

    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "offset": offset,
        "limit": limit
    }

    retry_count = 0

    while retry_count <= max_retries:
        try:
            response = requests.get(results_url, headers=headers, params=params)

            # Check if it's a 504 error and we haven't exceeded max retries
            if response.status_code == 504 and retry_count < max_retries:
                retry_count += 1
                print(f"Received 504 error, attempt {retry_count} of {max_retries}. Retrying in {retry_delay} seconds ...")

                # Exponential backoff
                backoff_delay = retry_delay * (2 ** (retry_count - 1))
                time.sleep(backoff_delay)
                continue

            # If it's not a 504 error or we've exceeded retries, raise HTTPError for client/server errors
            response.raise_for_status()

            # Return the parsed JSON response
            return response.json()
        except requests.exceptions.RequestException as error:
            handle_error(error)  # Log the error using handle_error
            raise


def handle_error(error):
    """
    Handles known errors based on HTTP response status codes.

    Inspects the error object returned by an HTTP request (using the `requests` library)
    and logs a corresponding error message based on the HTTP status code.

    Args:
        error (requests.exceptions.RequestException): The error object caught during the request.

    Returns:
        None: This function doesn't return any value, it logs errors to the console.
    """
    if hasattr(error, 'response') and error.response:
        status_code = error.response.status_code
        if status_code == 400:
            print("Bad Request: Please check the job ID or request parameters.")
        elif status_code == 401:
            print("Unauthorized: Check your authorization token.")
        elif status_code == 403:
            print("Forbidden: You do not have access to this resource.")
        elif status_code == 404:
            print("Not Found: The specified job ID does not exist or has no results.")
        elif status_code == 429:
            print("Too Many Requests: You are being rate limited. Try again later.")
        elif status_code == 500:
            print("Internal Server Error: Something went wrong on the server.")
        else:
            print(f"Error {status_code}: {error.response.text}")
    else:
        print("Error:", str(error))
