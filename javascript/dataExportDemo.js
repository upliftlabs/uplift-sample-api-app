import axios from "axios";

// Replace with your actual jobId and authorization token
const token = process.env.UPLIFT_API_KEY;
const exportUrl = process.env.UPLIFT_DATA_EXPORT_URL;

// Function to create data export job
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

// Function to get job status
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

// Function to get job result
async function getJobResult(jobId, offset, limit) {
	if (!jobId) {
		console.log("Error: jobId is required in getJobStatus");
		return;
	}

	let resultUrl = `${exportUrl}/job/${jobId}/result`;

	console.log("#####	resultUrl:",  resultUrl, offset, limit);

	try {
		const response = await axios.get(
			resultUrl,
			{
				headers: {
					'Authorization': `Bearer ${token}`
				},
				params: {
					offset,
					limit
				}
			}
		);
		return response.data;
	} catch (error) {
		handleError(error);
		throw error; // Re-throw to allow exit from loop in case of non-recoverable error
	}
}

// Function to handle known errors
function handleError(error) {
	if (error.response) {
		switch (error.response.status) {
		case 400:
			console.error("Bad Request: Please check the job ID or request parameters.");
			break;
		case 401:
			console.error("Unauthorized: Check your authorization token.");
			break;
		case 403:
			console.error("Forbidden: You do not have access to this resource.");
			break;
		case 404:
			console.error("Not Found: The specified job ID does not exist or has no result.");
			break;
		case 429:
			console.error("Too Many Requests: You are being rate limited. Try again later.");
			break;
		case 500:
			console.error("Internal Server Error: Something went wrong on the server.");
			break;
		default:
			console.error(`Error ${error.response.status}:`, error.response.data);
		}
	} else {
		console.error("Error:", error.message);
	}
}

// Function to retrieve export data
async function getExportData(jobId, offset, limit) {
	let result;
	try {
		let status;
		do {
			status = await getJobStatus(jobId);
			console.log("##### check status:", status);

			if (status === 'COMPLETED') {
				// Job is complete, proceed to get the result
				result = await getJobResult(jobId, offset, limit);
				break;
			} else if (status === 'FAILED' || status === 'CANCELED') {
				// Handle failed or canceled status as errors
				console.error(`Job ${status}. Unable to retrieve result.`);
				return;
			} else if (status === 'RUNNING') {
				// Wait for a few seconds before checking status again
				await new Promise(resolve => setTimeout(resolve, 5000));
			} else {
				// Unexpected status
				console.error(`Unexpected Job Status: ${status}`);
				break;
			}
		} while (status === 'RUNNING');
		return result;
	} catch (error) {
		console.error("An error occurred while checking job status or retrieving result.");
	}
}

// Prepare the list of activity/movement that to get export data from
const categories = [
	{ activity: "baseball"	   , movement:	"hitting"	   },
	{ activity: "baseball"	   , movement:	"pitching"	   }
];

// The start of the time range for data retrieval in epoch time (UTC).
// Defaults to 24 hours prior to reduce the volume of data exported.
let startTime = 1604807785;

// The end of the time range for data retrieval in epoch time (UTC).
// Defaults to the current time to provide up-to-date information.
let endTime;

// dateMode: "last_modified" or "capture_time"
let dateMode = "last_modified";

// Number of rows to skip for result pagination. Default is 0.
let offset = 0;

// Number of rows to retrieve. Maximum valid value is 500. Default is 100. 
let limit = 500;

// Start the process
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
