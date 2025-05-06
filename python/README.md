# Uplift Sample API App (Python Version)

This is a simple demo app that shows how you can use the Uplift APIs with Python.

## Prerequisites

### Installing Python

To run this sample app, you’ll need Python installed on your system.

1. **Minimum Python Version**: The application requires Python **3.8 or higher**.
2. **Where to Download Python**:
   - Visit the [Python official website](https://www.python.org/).
   - Download and install the latest stable version.

## Folder Structure

The Python app organizes the files as follows:
```
python/
├── app.py                # Main script to start the data export process
├── api.py                # Contains functions for API interaction
├── files.py              # Contains file handling and CSV export logic
├── requirements.txt      # Python dependencies for the project
└── README.md             # This file

```

### Installing Dependencies

Install the dependencies using [pip](https://pip.pypa.io/en/stable/) in this directory:

```bash
    $ pip install -r requirements.txt
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

Before starting the app, you need to set the following variables in the `app.py` file. These are critical for defining the data export process:

1. **Categories (Activity and Movement)**: A list of activities and movements for which you want to retrieve data.
   - Example:
     ```python
     categories = [
         {"activity": "baseball", "movement": "hitting"},
         {"activity": "baseball", "movement": "pitching"}
     ]
     ```

2. **Time Range (Start and End Time)**: Set the start and end time in epoch format for the data you wish to retrieve.
   - Example:
     ```python
     start_time = 1604807785  # 24 hours ago
     end_time = int(time.time())  # Current time
     ```

3. **Date Mode**: Define how to filter the data. You can choose between `last_modified` or `capture_time`.
   - Example:
     ```python
     date_mode = "last_modified"  # Use 'capture_time' for the actual capture time
     ```

4. **Pagination Settings**: Set the pagination parameters to control how many rows to fetch and skip.
   - Example:
     ```python
     offset = 0  # Default is 0
     limit = 500  # Maximum rows per request (default is 500)
     ```

Make sure to adjust these variables according to the data you're interested in exporting. The following parameters are passed to the `create_export_job` function:

```python
data = {
    "activity": category["activity"],
    "movement": category["movement"],
    "start_time": start_time,
    "end_time": end_time,
    "date_mode": date_mode
}
```

The `create_export_job` function also supports additional data filtering options through the following optional parameters:

- `athletes`: Filter data by specific athlete IDs
- `metrics`: Limit the export to specific metrics
- `row_filter_column`: Specify a column to filter rows

For more details, please refer to the [API Reference](https://docs.uplift.ai/api-reference/data/export/create).

Here is an example that includes these optional parameters:

```python
data = {
    "activity": category["activity"],
    "movement": category["movement"],
    "start_time": start_time,
    "end_time": end_time,
    "date_mode": date_mode,
    "athletes": [
        "athlete_id1",
        "athlete_id2"
    ],
    "metrics": [
        "metric1",
        "metric2"
    ],
    "row_filter_column": "column_name"
}
```

### Starting the App
Once you've installed the dependencies, set up the API key, and configured the variables in `app.py`, you can start the app by running the following command in your terminal:
```
$ python app.py
```
For more details on how the app works, the usage, and the output of the export process, please refer to the [Sample App Usage (NodeJS and Python)](../README.md#sample-app-usage-nodejs-and-python) section in the main `README.md`.

### More Info
For additional information and explanations, please refer to the comments within the files.
