# Uplift Sample API App

This is a simple demo app that shows how you can use the Uplift APIs

## Running the App

First, install dependencies using pip3 -

```
$ pip3 install aiohttp
```

Next, add your own API Key and Uplift data export URL to the environment variables.
There are a few ways to do this but the simplest would be to do it right in your shell.

```
$ export UPLIFT_API_KEY=<key>
$ export UPLIFT_DATA_EXPORT_UR=<url>
```

Finally, start the app using python

```
$ python3 dataExportDemo.py
```

## Walkthrough

### dataExportDemo.py

The first thing for data export is to create a data export job -

```python
async def create_export_job(session, data):
    try:
        async with session.post(export_url, json=data, headers=headers) as response:
            response_data = await response.json()
            return response_data.get("jobId")
    except Exception as e:
        handle_error(e)
```

Next the app checks status of the newly created job -

```python
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
```

Now we are ready to retrieve data result if the job status returned is COMPLETED -

```python
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
```

Finally, we can loop through the list of categories that we want to export data from and write the
the result to files if needed -

```python
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
```

### More Info
For more details, read the comments in the file
