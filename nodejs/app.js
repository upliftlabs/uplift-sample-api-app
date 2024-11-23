import {readEnvJson, writeCsvFile} from "./file.js";
import {createExportJob, getJobStatus, getJobResult} from './api.js'


/**
 * Function to check the status of a job and ensure it completes successfully.
 *
 * This function continuously checks the status of a job by calling the `getJobStatus` API.
 * It keeps polling the job status every few seconds until the job is either completed, failed, or canceled.
 * If the job completes successfully, it returns `true`. If the job fails or is canceled, it throws an error.
 * It also handles unexpected job statuses by throwing an error with the unexpected status.
 *
 * @param {string} apiKey - The API key to authorize the request.
 * @param {string} dataURL - The base URL for the API endpoint.
 * @param {string} jobId - The ID of the job whose status is being checked.
 *
 * @returns {Promise<boolean>} - Returns `true` if the job is completed successfully, throws an error if the job fails or is canceled.
 */
const checkJobStatus = async (apiKey, dataURL, jobId) => {
	let status;
	// Continuously check the job status until it completes, fails, or is canceled
	do {
		status = await getJobStatus(apiKey, dataURL, jobId);
		console.log("Checking job status:", status);
		if (status === 'COMPLETED') {
			// Job has completed successfully
			console.log("Job completed successfully.");
			return true; // Return 'COMPLETED' to indicate the job is finished
		} else if (status === 'FAILED' || status === 'CANCELED') {
			// Handle failed or canceled status as errors
			throw new Error(`Job ${status}. Unable to retrieve result.`);
		} else if (status === 'RUNNING') {
			// Wait for a few seconds before checking status again if the job is still running
			console.log("Job is still running. Checking again in 5 seconds...");
			await new Promise(resolve => setTimeout(resolve, 5000)); // 5-second delay
		} else {
			// Unexpected status
			throw new Error(`Unexpected Job Status: ${status}`);
		}
	} while (status === 'RUNNING');
}

/**
 * Function to handle the export of data from a paginated API into CSV files.
 * It accumulates rows for each unique combination of athleteId and sessionId,
 * and writes them to separate CSV files. The folder structure is organized by athleteId,
 * with CSV files for each sessionId inside each athlete's folder. Pagination is handled to
 * continue fetching data until all rows are retrieved.
 *
 * The function ensures that only the headers are written once per sessionId, and
 * subsequent rows are appended to the respective CSV file for each session.
 * If the athleteId or sessionId changes, the current data is saved, and a new file is started.
 *
 * @param {string} apiKey - The API key used for authentication in the API requests.
 * @param {string} dataURL - The base URL for the data source.
 * @param {string} jobId - The job ID to fetch the result.
 * @param {number} [offset=0] - The offset to use for pagination (default is 0).
 * @param {number} [limit=500] - The limit of rows to fetch per API request (default is 500).
 *
 * @throws {Error} - Throws an error if there is a problem during data fetching or file writing.
 */
const handleDataExport = async (apiKey, dataURL, jobId, offset = 0, limit = 500) => {
	let sessionId = null; // Initially there is no sessionId
	let athleteId = null; // Initially there is no athleteId
	let rowsToWrite = [];  // Will accumulate rows for the current sessionId and athleteId

	try {
		while (true) {
			// Fetch the paginated result from the API
			const result = await getJobResult(apiKey, dataURL, jobId, offset, limit);

			if (!result || result.rows.length === 0) {
				break; // No more rows to fetch, exit the loop
			}

			// Process each row and check if the sessionId or athleteId has changed
			for (const row of result.rows) {
				const currentSessionId = row.sessionid;
				const currentAthleteId = row.athleteid;

				// If athleteId or sessionId changes, save the accumulated rows and reset for the new sessionId or athleteId
				if (athleteId && athleteId !== currentAthleteId) {
					// Write data for the previous athleteId and sessionId before moving to the new athlete
					if (rowsToWrite.length > 0) {
						writeCsvFile(rowsToWrite, athleteId, sessionId);
						rowsToWrite = []; // Clear accumulated rows
					}
				}

				if (sessionId && sessionId !== currentSessionId) {
					// Write data for the previous sessionId before moving to the new session
					if (rowsToWrite.length > 0) {
						writeCsvFile(rowsToWrite, athleteId, sessionId);
						rowsToWrite = []; // Clear accumulated rows
					}
				}

				// Accumulate the row for the current athleteId and sessionId
				rowsToWrite.push(row);

				// Update the current sessionId and athleteId
				athleteId = currentAthleteId;
				sessionId = currentSessionId;
			}

			// Move the offset to the next page for pagination
			offset += result.rows.length;

			// Pause for 1 second before making the next API request (to avoid rate-limiting)
			await new Promise(resolve => setTimeout(resolve, 1000));
		}

		// After the loop, check if there are any rows left to save for the last sessionId and athleteId
		if (rowsToWrite.length > 0) {
			writeCsvFile(rowsToWrite, athleteId, sessionId);
		}
	} catch (error) {
		console.error("Error during data export:", error);
		throw new Error("Failed to export data due to an error in fetching or saving data.");
	}
}

// Function to handle the main process of creating jobs and retrieving export data
const handleExportProcess = async () => {
	// Call function to get API Key from the env.json file
	const {UPLIFT_API_KEY: apiKey, UPLIFT_DATA_URL: dataURL} = readEnvJson();
	if (!apiKey || !dataURL) {
		throw new Error('Missing API Key or Data URL from env.json.');
	}

	// Prepare the list of activity/movement that to get export data from
	const categories = [
		{activity: "baseball", movement: "hitting"},
		{activity: "baseball", movement: "pitching"}
	];

	// The start of the time range for data retrieval in epoch time (UTC).
	// Defaults to 24 hours prior to reduce the volume of data exported.
	let startTime = 1604807785;

	// The end of the time range for data retrieval in epoch time (UTC).
	// Defaults to the current time to provide up-to-date information.
	let endTime;

	// Mode for date filtering: "last_modified" or "capture_time"
	let dateMode = "last_modified";

	// Number of rows to skip for result pagination. Default is 0.
	let offset = 0;

	// Number of rows to retrieve. Maximum valid value is 500. Default is 100.
	let limit = 500;

	for (const category of categories) {
		console.log("## ", category.activity, category.movement);
		offset = 0;
		limit = 500;

		try {
			const data = {
				activity: category.activity,
				movement: category.movement,
				startTime,
				endTime,
				dateMode
			};
			const jobId = await createExportJob(apiKey, dataURL, data);
			console.log("Create job:", jobId);

			if (jobId) {
				// Check job status before proceeding
				const status = await checkJobStatus(apiKey, dataURL, jobId);
				if (status) {
					await handleDataExport(apiKey, dataURL, jobId, offset, limit)
				}
			}
		} catch (error) {
			// Catch any errors from createExportJob, checkJobStatus, or getJobResult
			console.error(`Error processing category: ${category.activity} - ${category.movement}:`, error);
			throw error;
		}
	}
}

// ==============================
// Start the process
// ==============================
handleExportProcess()
	.then(() => {
		console.log('Export process completed successfully!');
	})
	.catch((error) => {
		console.error('An error occurred during the export process:', error);
	});
