# Uplift API Sample Repo

Welcome to the Uplift API Sample Repo! This repository contains two versions of the sample application and a 3D transformation script:

1. **Node.js Version**  
   Designed for developers working with the Node.js runtime environment.

2. **Python Version**  
   Built for Python developers.

3. **3D Data Transformation Script**  
    A script that applies rotations and translations to 3D coordinates.


## Sample App Usage (NodeJS and Python)
#### Making API Calls and Handling Pagination
The app retrieves data from an API in paginated form. The function `getJobResult` will fetch a page of results, and pagination will continue until all data is retrieved.

#### Exporting Data to CSV
The app collects the data into CSV files. The data will be organized by athleteId and sessionId. For each combination of athleteId and sessionId, a folder will be created. If a new session starts, a new CSV file will be generated. If the session already exists, new rows will be appended to the file.

1. Directory Structure:
   * A folder will be created for each athleteId inside the `./data/` directory of the respective app version.
   * Inside each folder, a CSV file will be created (or appended) for each sessionId.

```
      data/                     # Folder where CSV files are saved
      └── athlete_id/           # Folder for each athlete, named by athleteId
          └── session_id.csv    # CSV file for each session, named by sessionId
```
2. CSV File Structure:
   * The first row in each CSV file will contain the headers (column names).
   * Each subsequent row will contain the data values for that particular session.


### Structure of the Returned Data

The app works with the results returned from the API, which follow this structure:

#### Response Format:

    {
        "jobId": "<string>",
        "rowCount": <int>,
        "schema": [
            {
                "name": "<string>",
                "type": {
                    "name": "<string>"
                }
            }
        ],
        "rows": [
            {}
        ]
    }

#### Explanation:

- **jobId** (string): A unique identifier for the export job. This ID can be used to track the progress or check the status of the job.

- **rowCount** (integer): The number of rows returned in this specific API response.

- **schema** (array of objects): This defines the structure of the data. Each object contains:
   - **name** (string): The name of the column.
   - **type** (object):
      - **name** (string): The data type of the column, such as string, integer, etc.

- **rows** (array of objects): This contains the actual data returned by the API. Each object in the `rows` array represents a single data entry, where each entry corresponds to a column defined in the `schema`.

### Documentation

Each version of the application has its own dedicated `README.md` file. You can find them in their respective directories:

- [Node.js Version Documentation](./nodejs/README.md)
- [Python Version Documentation](./python/README.md)

Please refer to the specific documentation for details on installation, usage, and configuration.

## 3D Data Transformation Script Usage

The 3D Data Transformation Script applies rotations and translations to 3D coordinates for a given dataset.

### Documentation

For detailed instructions on how to use the 3D Data Transformation, including setup, configuration, and customization, refer to the specific `README.md` file . You can find it in the `utilities` directory:

- [3D Data Transformation Documentation](./utilities/README.md)

