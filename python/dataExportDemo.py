import asyncio
import aiohttp
import os
import time

# Environment variables for sensitive information
token = os.getenv("UPLIFT_API_KEY")
export_url = os.getenv("UPLIFT_DATA_EXPORT_URL")

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Function to create data export job
async def create_export_job(session, data):
    try:
        async with session.post(export_url, json=data, headers=headers) as response:
            response_data = await response.json()
            return response_data.get("jobId")
    except Exception as e:
        handle_error(e)

# Function to get job status
async def get_job_status(session, job_id):
    if not job_id:
        print("Error: jobId is required in get_job_status")
        return None

    status_url = f"{export_url}/job/{job_id}"

    try:
        async with session.get(status_url, headers=headers) as response:
            response_data = await response.json()
            return response_data.get("status")
    except Exception as e:
        handle_error(e)

# Function to get job result
async def get_job_result(session, job_id, offset, limit):
    if not job_id:
        print("Error: jobId is required in get_job_result")
        return None

    result_url = f"{export_url}/job/{job_id}/result"
    print("##### resultUrl:", result_url, offset, limit)
    
    params = {'offset': offset, 'limit': limit}

    try:
        async with session.get(result_url, headers=headers, params=params) as response:
            return await response.json()
    except Exception as e:
        handle_error(e)

# Function to handle known errors
def handle_error(error):
    if hasattr(error, 'response') and error.response is not None:
        status = error.response.status
        if status == 400:
            print("Bad Request: Please check the job ID or request parameters.")
        elif status == 401:
            print("Unauthorized: Check your authorization token.")
        elif status == 403:
            print("Forbidden: You do not have access to this resource.")
        elif status == 404:
            print("Not Found: The specified job ID does not exist or has no result.")
        elif status == 429:
            print("Too Many Requests: You are being rate limited. Try again later.")
        elif status == 500:
            print("Internal Server Error: Something went wrong on the server.")
        else:
            print(f"Error {status}: {error.response.text}")
    else:
        print("Error:", str(error))

# Function to retrieve export data
async def get_export_data(session, job_id, offset, limit):
    while True:
        status = await get_job_status(session, job_id)
        print("##### check status:", status)

        if status == "COMPLETED":
            result = await get_job_result(session, job_id, offset, limit)
            return result
        elif status in ["FAILED", "CANCELED"]:
            print(f"Job {status}. Unable to retrieve result.")
            return None
        elif status == "RUNNING":
            await asyncio.sleep(5)
        else:
            print(f"Unexpected Job Status: {status}")
            return None

async def main():
    # Prepare the list of activity/movement that to get export data from
    categories = [
        {"activity": "baseball", "movement": "hitting"},
        {"activity": "baseball", "movement": "pitching"}
    ]

    # The start of the time range for data retrieval in epoch time (UTC).
    # Defaults to 24 hours prior to reduce the volume of data exported.
    start_time = 1604807785

    # The end of the time range for data retrieval in epoch time (UTC).
    # Defaults to the current time to provide up-to-date information.
    end_time = int(time.time())  # Use the current time

    # dateMode: "last_modified" or "capture_time"
    date_mode = "last_modified"

    # Number of rows to skip for result pagination. Default is 0.
    offset = 0

    # Number of rows to retrieve. Maximum valid value is 500. Default is 100. 
    limit = 500

    # Start the process
    async with aiohttp.ClientSession() as session:
        for category in categories:
            print("##", category["activity"], category["movement"])

            job_data = {
                "activity": category["activity"],
                "movement": category["movement"],
                "startTime": start_time,
                "endTime": end_time,
                "dateMode": date_mode
            }

            job_id = await create_export_job(session, job_data)
            print("##### create job:", job_id)

            if job_id:
                while True:
                    result = await get_export_data(session, job_id, offset, limit)
                    if not result or "rows" not in result:
                        break

                    print("##### got result:", len(result["rows"]))

		    # Write the result to file if needed. The format of the result:
                    #	   {
		    #		   "jobId": "<string>",
		    #		   "rowCount": <int>,
		    #		   "schema": [
		    #			   {
		    #				   "name": "<string>",
		    #				   "type": {
		    #					   "name": "<string>"
		    #				   }
		    #			   }
		    #		   ],
		    #		   "rows": [
		    #			   {}
		    #		   ]
		    #	   }

                    offset += len(result["rows"])

if __name__ == "__main__":
    asyncio.run(main())
