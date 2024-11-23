import fs from 'fs';
import { stringify } from 'csv-stringify/sync';

/**
 * Function to read and parse the contents of the `env.json` file.
 *
 * This function synchronously reads the `env.json` file, parses its content, and returns the parsed data
 * as a JavaScript object. If the file cannot be read or parsed, it throws an error with a descriptive message.
 *
 * @returns {Object} - The parsed JSON content from the `env.json` file.
 *
 * @throws {Error} - Throws an error if the file cannot be read or the JSON content is invalid.
 */
export const readEnvJson = () => {
    try {
        const data = fs.readFileSync('./env.json', 'utf-8');
        return JSON.parse(data); // Parse and return the JSON content
    } catch (error) {
        throw new Error('Error reading or parsing env.json: ' + error.message); // Return null if there's an error
    }
}

/**
 * Function to write rows of data to a CSV file, creating necessary directories
 * based on athleteId and sessionId.
 *
 * The function will create a folder for each athleteId and store the CSV file for
 * each sessionId in that folder. If the CSV file already exists, it will append
 * the new rows to the file. If the file doesn't exist, it will create a new file
 * with headers.
 *
 * @param {Array} rows - Array of row objects to be written to the CSV file.
 * @param {string} athleteId - The ID of the athlete. Used to create a folder.
 * @param {string} sessionId - The ID of the session. Used to create a file for each session.
 *
 * @throws {Error} - Throws an error if there is a problem with file system operations
 *                   or if the CSV stringification fails.
 */
export const writeCsvFile = (rows, athleteId, sessionId) => {
    // Create the folder path for the athleteId
    const folderPath = `./data/${athleteId}`; // Athlete-specific folder

    try {
        // Ensure the folder exists, create it if it doesn't
        if (!fs.existsSync(folderPath)) {
            fs.mkdirSync(folderPath, { recursive: true });
            console.log(`Created folder for athleteId: ${athleteId}`);
        }
    } catch (err) {
        console.error(`Error creating folder for athleteId ${athleteId}:`, err);
        throw new Error(`Failed to create folder for athleteId ${athleteId}: ${err.message}`);
    }

    // Define the path for the session CSV file
    const filePath = `${folderPath}/session_${sessionId}.csv`;

    // Extract headers from the first row
    const headers = Object.keys(rows[0]);

    try {
        // Convert rows to CSV format using synchronous stringification
        const output = stringify(rows, { header: true, columns: headers });

        try {
            // If the file already exists, append new rows; otherwise, create the file with headers.
            fs.appendFileSync(filePath, output);
            console.log(`CSV file written/updated for athleteId: ${athleteId}, sessionId: ${sessionId}`);
        } catch (fileErr) {
            console.error(`Error writing to file ${filePath}:`, fileErr);
            throw new Error(`Failed to write to CSV file: ${fileErr.message}`);
        }
    } catch (stringifyErr) {
        console.error('Error stringifying rows:', stringifyErr);
        throw new Error(`Failed to stringify rows for CSV: ${stringifyErr.message}`);
    }
}
