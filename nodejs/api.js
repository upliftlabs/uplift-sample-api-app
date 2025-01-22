import axios from "axios";

/**
 * Function to create a data export job
 *
 * Sends a POST request to the provided `dataURL` to initiate the export job
 * with the given parameters.
 *
 * @param {string} apiKey - The API key used for authentication.
 * @param {string} dataURL - The URL to send the POST request to.
 * @param {object} data - The payload for the export job request (e.g., activity, movement, date range).
 * @param {number} maxRetries - Maximum number of retry attempts (default: 3)
 * @param {number} retryDelay - Delay between retries in milliseconds (default: 2000)
 *
 * @returns {string} - The `jobId` string if the job is successfully created.
 *
 * @throws {Error} - Throws an error if the job creation fails (network issues, invalid API key, etc.).
 */
export const createExportJob = async (apiKey, dataURL, data, maxRetries = 3, retryDelay = 2000) => {
	let retryCount = 0;

	const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

	const makeRequest = async () => {
		try {
			const response = await axios.post(
				dataURL,
				data,
				{
					headers: {
						'Authorization': `Bearer ${apiKey}`,
						'Content-Type': 'application/json'
					}
				}
			);
			return response.data.jobId;
		} catch (error) {
			// Check if it's a 504 error and we haven't exceeded max retries
			if (error.response?.status === 504 && retryCount < maxRetries) {
				retryCount++;
				console.log(`Received 504 error, attempt ${retryCount} of ${maxRetries}. Retrying in ${retryDelay}ms ...`);

				// Exponential backoff
				const backoffDelay = retryDelay * Math.pow(2, retryCount - 1);
				await delay(backoffDelay);

				// Recursive retry
				return makeRequest();
			}

			// If it's not a 504 error or we've exceeded retries, handle the error
			handleError(error);
			throw error;
		}
	}

	return makeRequest();
}

/**
 * Function to get the status of a job
 *
 * Sends a GET request to the provided `dataURL` to retrieve the status of the job
 * identified by `jobId`.
 *
 * @param {string} apiKey - The API key used for authentication.
 * @param {string} dataURL - The URL of the API where the job status can be checked.
 * @param {string} jobId - The ID of the job whose status is being checked.
 * @param {number} maxRetries - Maximum number of retry attempts (default: 3)
 * @param {number} retryDelay - Delay between retries in milliseconds (default: 2000)
 *
 * @returns {string} - The job's status (e.g., 'RUNNING', 'COMPLETED', 'FAILED').
 *
 * @throws {Error} - Throws an error if the status retrieval fails (e.g., network errors or invalid API key).
 */
export const getJobStatus = async (apiKey, dataURL, jobId, maxRetries = 3, retryDelay = 2000)  => {
	if (!jobId) {
		console.log("Error: jobId is required in getJobStatus");
		return;
	}

	const statusUrl = `${dataURL}/job/${jobId}`;

	let retryCount = 0;

	const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

	const makeRequest = async () => {
		try {
			const response = await axios.get(
				statusUrl,
				{
					headers: {
						'Authorization': `Bearer ${apiKey}`
					}
				}
			);
			return response.data.status;
		} catch (error) {
			// Check if it's a 504 error and we haven't exceeded max retries
			if (error.response?.status === 504 && retryCount < maxRetries) {
				retryCount++;
				console.log(`Received 504 error, attempt ${retryCount} of ${maxRetries}. Retrying in ${retryDelay}ms ...`);

				// Exponential backoff
				const backoffDelay = retryDelay * Math.pow(2, retryCount - 1);
				await delay(backoffDelay);

				// Recursive retry
				return makeRequest();
			}

			// If it's not a 504 error or we've exceeded retries, handle the error
			handleError(error);
			throw error;
		}
	}

	return makeRequest();
}

/**
 * Function to get the results of a job
 *
 * Sends a GET request to the provided `dataURL` to retrieve the results of the job
 * identified by `jobId`. The request includes pagination parameters for `offset` and `limit`.
 *
 * @param {string} apiKey - The API key used for authentication.
 * @param {string} dataURL - The URL of the API where the job results can be fetched.
 * @param {string} jobId - The ID of the job whose results is being retrieved.
 * @param {number} offset - The number of rows to skip for results pagination.
 * @param {number} limit - The number of rows to retrieve in the response.
 * @param {number} maxRetries - Maximum number of retry attempts (default: 3)
 * @param {number} retryDelay - Delay between retries in milliseconds (default: 2000)
 *
 * @returns {object} - The results data of the job, including rows and metadata.
 *
 * @throws {Error} - Throws an error if the results retrieval fails (e.g., network errors, invalid API key).
 */
export const getJobResults = async (apiKey, dataURL, jobId, offset, limit, maxRetries = 3, retryDelay = 2000)  => {
	if (!jobId) {
		console.log("Error: jobId is required in getJobStatus");
		return;
	}

	let resultsUrl = `${dataURL}/job/${jobId}/results`;
	console.log(`resultsUrl: ${resultsUrl} | offset: ${offset} | limit: ${limit}`);

	let retryCount = 0;

	const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

	const makeRequest = async () => {
		try {
			const response = await axios.get(
				resultsUrl,
				{
					headers: {
						'Authorization': `Bearer ${apiKey}`
					},
					params: {
						offset,
						limit
					}
				}
			);
			return response.data;
		} catch (error) {
			// Check if it's a 504 error and we haven't exceeded max retries
			if (error.response?.status === 504 && retryCount < maxRetries) {
				retryCount++;
				console.log(`Received 504 error, attempt ${retryCount} of ${maxRetries}. Retrying in ${retryDelay}ms ...`);

				// Exponential backoff
				const backoffDelay = retryDelay * Math.pow(2, retryCount - 1);
				await delay(backoffDelay);

				// Recursive retry
				return makeRequest();
			}

			// If it's not a 504 error or we've exceeded retries, handle the error
			handleError(error);
			throw error;
		}
	}

	return makeRequest();
}

/**
 * Function to handle known errors based on HTTP response status codes.
 *
 * This function inspects the error object returned by an HTTP request (from Axios)
 * and logs a corresponding error message based on the HTTP status code.
 *
 * @param {Object} error - The error object caught during the request.
 * @param {Object} error.response - The HTTP response object containing status and data.
 * @param {string} error.message - The error message in case of a network error.
 *
 * @returns {void} - This function doesn't return any value, it logs errors to the console.
 */
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
			console.error("Not Found: The specified job ID does not exist or has no results.");
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
