# Uplift Sample API App

This is a simple demo app that shows how you can use the Uplift APIs

## Running the App

First, download the dependencies using [npm](https://www.npmjs.org) in this directory.

```
$ npm install
```

Next, add your own API Key and Uplift data export URL to the environment variables.
There are a few ways to do this but the simplest would be to do it right in your shell.

```
$ export UPLIFT_API_KEY=<key>
$ export UPLIFT_DATA_EXPORT_UR=<url>
```

Finally, start the app using node

```
$ node dataExportDemo.js
```

## Walkthrough

### dataExportDemo.js

The first thing for data export is to create a data export job -

```javascript
async function createExportJob(data) {
        try {
                const response = await axios.post(
                        exportUrl,
                        data,
                        {
                                headers: {
                                        'Authorization': `Bearer ${token}`,
                                        'Content-Type': 'application/json'
                                }
                        }
                );
                return response.data.jobId;
        } catch (error) {
                handleError(error);
                throw error; // Re-throw to allow exit from loop in case of non-recoverable error 
        }
}
```

Next the app checks status of the newly created job -

```javascript
async function getJobStatus(jobId) {
        if (!jobId) {
                console.log("Error: jobId is required in getJobStatus");
                return;
        }

        const statusUrl = `${exportUrl}/job/${jobId}`;

        try {
                const response = await axios.get(
                        statusUrl,
                        {
                                headers: {
                                        'Authorization': `Bearer ${token}`
                                }
                        }
                );
                return response.data.status;
        } catch (error) {
                handleError(error);
                throw error; // Re-throw to allow exit from loop in case of non-recoverable error
        }
}
```

Now we are ready to retrieve data result if the job status returned is COMPLETED -

```javascript
async function getJobResult(jobId, offset, limit) {
	if (!jobId) {
		console.log("Error: jobId is required in getJobStatus");
		return;
	}

	let resultUrl = `${exportUrl}/job/${jobId}/result`;

	let queryString = '?';
	if (offset >= 0) {
		queryString = `${queryString}offset=${offset.toString()}`;
	}
	if (limit >= 0) {
		if (queryString != '?') {
			queryString = queryString + '&';
		}
		queryString = `${queryString}limit=${limit.toString()}`
	}
	if (queryString != '?') {
		resultUrl = resultUrl + queryString;
	}
	console.log("#####	resultUrl:",  resultUrl);

	try {
		const response = await axios.get(
			resultUrl,
			{
				headers: {
					'Authorization': `Bearer ${token}`
				}
			}
		);
		return response.data;
	} catch (error) {
		handleError(error);
		throw error; // Re-throw to allow exit from loop in case of non-recoverable error
	}
}
```

Finally, we can loop through the list of categories that we want to export data from and write the
the result to files if needed -

```javascript
for (const e of categories) {
	console.log("## ", e.activity, e.movement);
	offset = 0;
	limit = 500;

	const jobId = await createExportJob({
		activity: e.activity,
		movement: e.movement,
		startTime,
		endTime,
		dateMode
	});
	console.log("##### create job:", jobId);

	if (jobId) {
		let result;
		do {
			result = await getExportData(jobId, offset, limit);
			if (!result) {
				break;
			}
			console.log("##### got result:", result.rows.length);

			// Write the result to file if needed. The format of the result:
			//	   {
			//		   "jobId": "<string>",
			//		   "rowCount": <int>,
			//		   "schema": [
			//			   {
			//				   "name": "<string>",
			//				   "type": {
			//					   "name": "<string>"
			//				   }
			//			   }
			//		   ],
			//		   "rows": [
			//			   {}
			//		   ]
			//	   }

			offset += result.rows.length;
		} while (result && result.rows.length > 0);
	}
}
```

### More Info
For more details, read the comments in the file
