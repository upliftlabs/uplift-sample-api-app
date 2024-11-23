import pandas as pd
import numpy as np
from scipy.spatial.transform import Rotation as R


def rotate_3d(data_3d_df, up_outofcamera):
    """
    Rotates 3D points in the given DataFrame based on a specified camera orientation.

    Parameters:
    ----------
    data_3d_df : pandas.DataFrame
        A DataFrame containing 3D points with columns like 'keypoint_1_x', 'keypoint_1_y', 'keypoint_1_z', etc.
        Each keypoint is represented by 3 columns, one for each coordinate (x, y, z).

    up_outofcamera : str
        The string representing the camera's orientation for the rotation, one of: '+y+x', '+y-z', '-y+z'.

    Returns:
    -------
    pandas.DataFrame
        Copy of DataFrame with rotated 3D coordinates.
    """
    # Define the rotation vectors based on the orientation
    # row - column ordering (up - out of camera)
    rotation_vectors = {
        '+y+x': [0, 90, 180],
        '+y-z': [0, 0, 180],
        '-y+z': [0, 0, 0]
    }
    rotation_vec = rotation_vectors[up_outofcamera]

    if not rotation_vec:
        return data_3d_df.copy()

    # Parse 3D points (Flat)
    points_3d_all = data_3d_df.filter(regex='_(x|y|z)$').copy()
    # Create Multi-level index
    points_3d_all.columns = points_3d_all.columns.str.split('_3d_', expand=True)

    # rotate 3D points
    r = R.from_euler('zyx', rotation_vec, degrees=True)
    for keypoint in points_3d_all.columns.get_level_values(0).unique():
        points_3d_all[keypoint] = r.apply(points_3d_all[keypoint].values)

    # Multi-level index back into a flat index
    points_3d_all.columns = points_3d_all.columns.map('_3d_'.join)
    # Update the original data frame with the rotated values
    data_3d_df.update(points_3d_all)

    return data_3d_df.copy()


def mean_and_reject_outliers(data, m=2):
    """
    Calculate the mean of the data after rejecting outliers.

    Data points with absolute deviations from the mean greater than
    `m` times the standard deviation are considered outliers and excluded.

    Parameters:
    -----------
    data : array-like
        The numerical data (e.g., list, numpy array, pandas series).

    m : float, optional (default=2)
        Multiplier for the standard deviation to define the outlier threshold.

    Returns:
    --------
    float
        The mean of the data after removing outliers, or 0 if no data points remain.

    Example:
    --------
    >> data = [1, 2, 3, 4, 100]
    >> mean_and_reject_outliers(data)
    2.5
    """
    data = np.array(data)
    mean = np.mean(data)
    std = np.std(data)
    # Mask out values that are within m standard deviations of the mean
    mask = np.abs(data - mean) < m * std
    # Apply the mask
    filtered_data = data[mask]
    # Return the mean of the filtered data, or 0 if no data points remain
    return np.mean(filtered_data) if filtered_data.size > 0 else 0


def transform_3d(data_3d_df, origin=None):
    """
    Shift 3D coordinates in the DataFrame relative to a new origin.

    If no origin is provided, the mean of the left hip's 3D coordinates is used as the origin.
    The function subtracts the origin from all 3D coordinates (x, y, z).

    Parameters:
    -----------
    data_3d_df : pandas DataFrame
        A DataFrame with 3D coordinates (columns ending in '_3d_x', '_3d_y', '_3d_z').

    origin : list or tuple, optional (default=None)
        New origin [x, y, z] to shift coordinates to. If None, the mean of the left hip's coordinates is used.

    Returns:
    --------
    pandas DataFrame
        The transformed DataFrame with coordinates adjusted to the new origin.
    """
    if origin is None:
        xvalue = mean_and_reject_outliers(data_3d_df['left_hip_jc_3d_x'].values)
        yvalue = mean_and_reject_outliers(data_3d_df['left_hip_jc_3d_y'].values)
        zvalue = mean_and_reject_outliers(data_3d_df['left_hip_jc_3d_z'].values)
        origin = [xvalue, yvalue, zvalue]

    data_3d_df[data_3d_df.filter(like='_3d_x').columns] = data_3d_df[data_3d_df.filter(like='_3d_x').columns] - origin[0]
    data_3d_df[data_3d_df.filter(like='_3d_y').columns] = data_3d_df[data_3d_df.filter(like='_3d_y').columns] - origin[1]
    data_3d_df[data_3d_df.filter(like='_3d_z').columns] = data_3d_df[data_3d_df.filter(like='_3d_z').columns] - origin[2]

    return data_3d_df.copy()


def apply_rotation_and_translation(data_df, up_outofcamera, origin):
    """
    Apply rotation and translation to the entire 3D DataFrame.

    This function first rotates the entire 3D data based on the specified
    camera orientation (up_outofcamera) and then translates the data by adjusting
    the coordinates relative to the provided origin.

    Parameters:
    -----------
    data_df : pandas DataFrame
        DataFrame containing 3D data to be rotated and translated.

    up_outofcamera : str
        The orientation of the camera for rotation (e.g., '+x+x', '-y+z').

    origin : list or tuple
        The origin [x, y, z] to translate the data.

    Returns:
    --------
    pandas DataFrame
        The rotated and translated 3D data.
    """
    # Apply rotation to the entire DataFrame
    data_df = rotate_3d(data_df, up_outofcamera)

    # Apply translation to the entire DataFrame
    data_df = transform_3d(data_df, origin)

    return data_df


def main():
    # Path to your CSV file
    file_path = '/path/to/your/csv/file.csv'
    
    # Path to the output CSV file
    output_file_path = '/path/to/save/output.csv'

    # Read the CSV file into a pandas DataFrame
    data_df = pd.read_csv(file_path)

    # Define the rotation orientation
    uplift_default_rotation = '+y-z'
    # Define the origin for the translation [x,y,z]; none will use left-hip
    uplift_default_origin = None

    # Apply rotation and translation to the entire DataFrame
    data_df_out = apply_rotation_and_translation(data_df, uplift_default_rotation, uplift_default_origin)

    # Save DataFrame to disk
    data_df_out.to_csv(output_file_path, index=False)

if __name__ == "__main__":
    main()
