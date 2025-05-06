# Uplift Sample API App (NodeJS Version)

This is a simple sample app that shows how you can use the Uplift APIs with NodeJS.

## Prerequisites
### Installing Node.js

To run this sample app, you'll need Node.js installed on your system.

1. **Minimum Node.js Version**: The application requires Node.js **16 or higher**.
2. **Where to Download Node.js**:
   - Visit the [Node.js official website](https://nodejs.org/).
   - Download and install the **LTS (Long-Term Support)** version, which is recommended for most users.

## Folder Structure

The Node.js app organizes the files as follows:
```
nodejs/
├── app.js                # Main script to start the data export process
├── api.js                # Contains functions for API interaction
├── files.js              # Contains file handling and CSV export logic
├── package.json          # Node.js dependencies and scripts
└── README.md             # This file

```

## Sample API App
### Installing Dependencies

Install the dependencies using [npm](https://www.npmjs.org) in this directory.

```
$ npm install
```

### Setting Up API Keys
In this directory, create a file named `env.json`.

```json
   {
     "UPLIFT_API_KEY": "your_api_key_here",
     "UPLIFT_DATA_URL": "https://uplift_data_url"
   }
```

### Setting the Variables

Before starting the app, you need to set the following variables in the `app.js` file. These are critical for defining the data export process:

1. **Categories (Activity and Movement)**: A list of activities and movements for which you want to retrieve data.
    - Example:
      ```javascript
      const categories = [
        { activity: "baseball", movement: "hitting" },
        { activity: "baseball", movement: "pitching" }
      ];
      ```

2. **Time Range (Start and End Time)**: Set the start and end time in epoch format for the data you wish to retrieve.
    - Example:
      ```javascript
      let startTime = 1604807785; // 24 hours ago
      let endTime = Math.floor(Date.now() / 1000); // Current time
      ```

3. **Date Mode**: Define how to filter the data. You can choose between `last_modified` or `capture_time`.
    - Example:
      ```javascript
      let dateMode = "last_modified"; // Use 'capture_time' for the actual capture time
      ```

4. **Pagination Settings**: Set the pagination parameters to control how many rows to fetch and skip.
    - Example:
      ```javascript
      let offset = 0; // Default is 0
      let limit = 500; // Maximum rows per request (default is 500)
      ```

Make sure to adjust these variables according to the data you're interested in exporting. The following parameters are passed to the `createExportJob` function:

```javascript
const data = {
  activity: category.activity,
  movement: category.movement,
  startTime,
  endTime,
  dateMode
};
```

The `createExportJob` function also supports additional data filtering options through the following optional parameters:

- `athletes`: Filter data by specific athlete IDs
- `metrics`: Limit the export to specific metrics
- `row_filter_column`: Specify a column to filter rows

For more details, please refer to the [API Reference](https://docs.uplift.ai/api-reference/data/export/create).

Here is an example that includes these optional parameters:

```javascript
const data = {
  activity: category.activity,
  movement: category.movement,
  startTime,
  endTime,
  dateMode,
  athletes: [
    "athlete_id1",
    "athlete_id2"
  ],
  metrics: [
    "metric1",
    "metric2"
  ],
  row_filter_column: "column_name"
};
```

### Starting the App
Once you've installed the dependencies, set up the API key, and configured the variables in `app.js`, you can start the app by running the following command in your terminal:
```
$ node app.js
```
For more details on how the app works, the usage, and the output of the export process, please refer to the [Sample App Usage (NodeJS and Python)](../README.md#sample-app-usage-nodejs-and-python) section in the main `README.md`.

### More Info
For additional information and explanations, please refer to the comments within the files.
