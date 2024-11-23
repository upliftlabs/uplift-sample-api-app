# 3D Data Transformation Script

## Overview

This Python script provides functionality to **rotate** and **translate** Uplift 3D data from the camera reference frame into the Uplift reference frame that is similarily used when downloading the session CSV files.


## Installing Dependencies
Install the dependencies using [pip](https://pip.pypa.io/en/stable/) in this directory:

```bash
pip install -r requirements.txt

```

## Running the Script
To run the script, follow these steps:

### 1. Update the `file_path` and `output_file_path`

Open the script and find the line where the CSV file is loaded:

```python
# Path to your CSV file
file_path = '/path/to/your/csv/file.csv'

# Path to the output CSV file
output_file_path = '/path/to/save/output.csv'
```
* Update the file_path variable to point to the location of your input CSV file.
* Update the output_file_path variable to specify where you want to save the transformed data.

Make sure to adjust both paths according to your system's file structure and your desired input/output locations.


### 2. Optional: Update the Rotation and Origin

You can customize the rotation and origin values that will be used in the transformation:

```python
uplift_default_rotation = '+y-z'

uplift_default_origin = None 
```

* The rotation value controls the camera orientation (e.g., '+y-z' or '-x+x').

* The origin value controls the point in space to which the 3D coordinates will be translated. If None, the origin will be automatically calculated based on the mean of the left hip coordinates.


### 3. Run the Script

Once you've updated the input/output file paths and any optional parameters, run the script by executing the following command:
```bash
    $ python transform_3d_data.py
```

This will process the CSV file, apply the rotation and translation transformations, and save the transformed data.

### 4. Check the Output

After running the script, the transformed data will be saved to the output file path you specified in the `output_file_path` variable. The script automatically writes the transformed DataFrame to this location.

Make sure the output_file_path is correctly set, for example:
```python
output_file_path = '/path/to/save/output.csv'
```

You can open the saved CSV file at the path you've set to inspect the transformed data.

## Notes

- The transformation assumes that the 3D coordinates are in the form of a DataFrame with specific naming conventions (e.g., `_3d_x`, `_3d_y`, `_3d_z`).
- The default origin for translation is the mean of the left hip joint coordinates (`left_hip_jc_3d_x`, `left_hip_jc_3d_y`, `left_hip_jc_3d_z`). If you'd like to use a different origin, you can pass it directly when calling `apply_rotation_and_translation()`.
