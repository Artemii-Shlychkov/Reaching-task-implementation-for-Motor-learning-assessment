# EXPERIMENTAL DATA PLOTTER
"""
This code is used to plot the experimental data from the csv file.
The data is read from the csv file and the error angles are plotted.
The perturbation, motor noise, and target angle sequences are detected and plotted.
The plot is saved in the same directory as the csv file.

"""

from tkinter import *

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import GUI

# Create a dialog window asking for the path to the csv file

dialog_window = Tk()
filepath = GUI.reader_menu(dialog_window)
print(filepath)


# Update this to your actual file path
# filepath = '/Users/a1/Desktop/exp_data/motor_noise_test/motor_noise_test_2024_03_18_16_31_58/motor_noise/experimental_data.csv'

def read_data(file_path):
    """Returns the data and the data folder.
    Args:
        file_path: Path to the file containing the data
    """
    # Read data from the specified file
    data = pd.read_csv(file_path)
    directory_path = '/'.join(file_path.split('/')[:-1])  # Get the directory path
    return data, directory_path


def subject_id(directory_path):
    """Returns the subject ID from the directory path.
    Args:
        directory_path: The directory path
    Returns:
        subject_id: The subject ID
    """
    subject_id = directory_path.split('/')[-2]  # Get the subject ID from the directory path
    return subject_id


def script_name(directory_path):
    """Returns the script name from the directory path.
    Args:
        directory_path: The directory path
    Returns:
        script_name: The script name
    """
    script_name = directory_path.split('/')[-1]  # Get the script name from the directory path
    return script_name


def remove_outliers(data, critical_angle):
    """ Function to remove outliers from the data.
    Args:
        data: The data to filter
        critical_angle: The critical angle in degrees to filter out the outliers. By default, should be chosen as 100
    Returns:
        filtered_data: The filtered data
        critical_idx: The indices of the critical angles
    """
    angle = np.radians(critical_angle)
    critical_idx = np.where(data.iloc[:, 1] > critical_angle)[0]
    filtered_data = data[np.abs(data.iloc[:, 1]) < angle]
    return filtered_data, critical_idx


def plot_error_angles():
    """
    Function to plot error angles.
    """
    ax1.plot(timeline, error_angles, 'bo-', alpha=0.75, label='error angles')


def convert_perurbation_mode(data):
    """Function to convert perturbation mode to numerical values.
        Args: data: The data to convert
        Returns: data: The data with the perturbation mode converted to numerical values
    """
    pd.set_option('future.no_silent_downcasting', True)
    data['perturbation_mode'] = data['perturbation_mode'].replace('False', 0)
    data['perturbation_mode'] = data['perturbation_mode'].replace('sudden', 1)
    data['perturbation_mode'] = data['perturbation_mode'].replace('gradual', 2)
    data['perturbation_mode'] = data['perturbation_mode'].replace('random', 3)
    return data


def convert_feedback_mode(data):
    """Function to convert feedback mode to numerical values.
        Args: data: The data to convert
        Returns: data: The data with the feedback mode converted to numerical values
    """
    pd.set_option('future.no_silent_downcasting', True)

    data['feedback'] = data['feedback'].replace('False', 0)
    data['feedback'] = data['feedback'].replace('trajectory', 1)
    data['feedback'] = data['feedback'].replace('end_pos', 2)
    data['feedback'] = data['feedback'].replace('reinforcement', 3)
    return data


def mode_boundaries(mode):
    """ Function to identify the boundaries of perturbation, motor noise, target sequences in the data.
    Args:
        data['column_name']: The column to filter and analyze, e.g.:
            data['perturbation_mode']: The perturbation sequence
            data['motor_noise']: The motor noise sequence
            data['sequence_target']: The target angle sequence
    Returns: boundaries: 3-dimensional array with the boundaries of sequences and sequence parameter:
        boundaries[:,0]: The start index of the sequence
        boundaries[:,1]: The end index of the sequence
        boundaries[:,2]: The sequence parameter: type of perturbation ('gradual', 'sudden', 'random'), motor noise level or
        target angle
    """

    column_name = mode  # Specify the mode (column) to filter and analyze

    filtered_data = data[data[column_name] != 0]

    filtered_attempts = filtered_data['attempts'].values  # attempts of corresponding mode
    filtered_values = filtered_data[column_name].values  # values of corresponding mode

    # Calculate differences in attempts and values to identify changes
    difference_in_attempts = np.diff(filtered_attempts) - 1
    difference_in_values = np.diff(filtered_values)

    # Initialize boundaries array
    boundaries = np.zeros((0, 3), dtype=object)

    # If there are differences in attempts, identify sequences of consecutive attempts

    if not np.all(difference_in_attempts == 0):

        start_idx_attempts = np.where(difference_in_attempts != 0)[0] + 1
        start_idx_attempts = np.insert(start_idx_attempts, 0, 0)  # Include the first sequence start

        end_idx_attempts = np.where(difference_in_attempts != 0)[0]
        end_idx_attempts = np.append(end_idx_attempts, len(filtered_attempts) - 1)  # Include the last sequence end

        boundaries = np.zeros((len(start_idx_attempts), 3), dtype=object)
        for i in range(len(start_idx_attempts)):
            start_idx = filtered_attempts[start_idx_attempts[i]] - 1

            end_idx = filtered_attempts[end_idx_attempts[i]]
            boundaries[i, 0] = start_idx
            boundaries[i, 1] = end_idx  # Adjust end index to include the attempt in the sequence
            boundaries[i, 2] = filtered_values[start_idx_attempts[i]]
    else:
        # If no differences in attempts, potentially handle changes of values in specified column

        start_idx_values = np.where(difference_in_values != 0)[0] + 1
        start_idx_values = np.insert(start_idx_values, 0, 0)  # Include the first sequence start
        end_idx_values = np.where(difference_in_values != 0)[0]
        end_idx_values = np.append(end_idx_values, len(filtered_values) - 1)  # Include the last sequence end
        boundaries = np.zeros((len(start_idx_values), 3), dtype=object)

        for i in range(len(start_idx_values)):
            start_idx = filtered_attempts[start_idx_values[i]] - 1
            end_idx = filtered_attempts[end_idx_values[i]]
            boundaries[i, 0] = start_idx
            boundaries[i, 1] = end_idx  # Adjust end index to include the attempt in the sequence
            boundaries[i, 2] = filtered_values[start_idx_values[i]]
    return boundaries


data, path = read_data(filepath)  # read data
data, _ = remove_outliers(data, 100)  # remove outliers
data = convert_perurbation_mode(data)  # convert perturbation mode to numerical values
data = convert_feedback_mode(data)  # convert feedback mode to numerical values
error_angles = data['error_angle']  # error angles values
timeline = data['attempts'].values  # attempts values

# plot figure
fig, ax1 = plt.subplots(figsize=(20, 7.5))

# figure specs
y_lim_max = float("{:.1f}".format((max(np.max(error_angles), np.abs(np.min(error_angles))) + 0.1)))
y_lim_min = -y_lim_max
x_length = len(timeline)
y_length = y_lim_max - y_lim_min
ax = plt.gca()
ax1.set_ylim(y_lim_min, y_lim_max)

# plot secondary y-axis for total perturbation
if not np.all(data['total_perturbation'].values == 0):
    ax2 = ax.twinx()
    ax2.plot(timeline, data['total_perturbation'], 'r-', alpha=0.2, label='total perturbation')
    y_ax2_min = np.min(data['total_perturbation'].values)
    y_ax2_max = np.max(data['total_perturbation'].values)
    ratio = y_length / (y_ax2_max - y_ax2_min) * 0.5
    ax2.set_ylim(min(y_lim_min * ratio, -0.6), max(y_lim_max * ratio, 0.6))
    ax2.set_yticks([-0.5, -0.25, 0, 0.25, 0.5])
    ax2.set_ylabel('Total perturbation (rad)')
else:
    ax2 = None
# plot error angles
plot_error_angles()

# plot perturbation regimes
if not np.all(data['perturbation_mode'].values == 0):
    perturbation_boundaries = mode_boundaries('perturbation_mode')
    perturbation_boundaries[perturbation_boundaries[:, 2] == 1, 2] = 'sudden'
    perturbation_boundaries[perturbation_boundaries[:, 2] == 2, 2] = 'gradual'
    perturbation_boundaries[perturbation_boundaries[:, 2] == 3, 2] = 'random'

    for i, perturbation in enumerate(perturbation_boundaries):
        perturbation_length = perturbation[1] - perturbation[0]
        ax1.fill_betweenx(ax1.get_ylim(), perturbation[0], perturbation[1], color='orange', alpha=0.15)
        ax1.text(perturbation[0] + perturbation_length / 2, y_lim_max - 0.2, f'{perturbation[2]}\n perturbation',
                 ha='center', va='center', alpha=0.75, color='orange', fontweight='bold')

# plot motor noise regimes
if not np.all(data['motor_noise'].values == 0):
    motor_noise_boundaries = mode_boundaries('motor_noise')

    for i, motor_noise in enumerate(motor_noise_boundaries):
        motor_length = motor_noise[1] - motor_noise[0]

        ax1.fill_betweenx((y_lim_min, y_lim_min + 0.1), motor_noise[0], motor_noise[1], color='red',
                          alpha=0.1 + motor_noise[2] / 25, label=f'motor noise: {motor_noise[2]}')
        ax1.text(motor_noise[0] + motor_length / 2, y_lim_min + 0.05, f'{motor_noise[2]}', va='center', ha='center',
                 fontweight='bold')

# plot target angle changes
sequence_target_boundaries = mode_boundaries('sequence_target')
for i, target in enumerate(sequence_target_boundaries):
    ax1.vlines(target[0], color='green', linestyle='-', linewidth=2, label='target angle\nchange' if i == 0 else '',
               ymin=y_lim_max - 0.1, ymax=y_lim_max)
    ax1.text(target[0], y_lim_max - 0.05, f'  {target[2]}°', va='center', ha='left',
             fontweight='bold', color='green')
    # ax1.arrow(target[0], y_lim_max - 0.1, x_length / 100, 0, linewidth=2, head_width=y_length / 50,
    #          head_length=x_length / 100, fc='green',
    #          ec='green')

# plot feedback regimes
if not np.all(data['feedback'].values == 0):
    feedback_boundaries = mode_boundaries('feedback')
    feedback_boundaries[feedback_boundaries[:, 2] == 1, 2] = 'trajectory'
    feedback_boundaries[feedback_boundaries[:, 2] == 2, 2] = 'end_pos'
    feedback_boundaries[feedback_boundaries[:, 2] == 3, 2] = 'reinforcement'

    for i, feedback in enumerate(feedback_boundaries):
        feedback_length = feedback[1] - feedback[0]

        ax1.fill_betweenx((y_lim_min + 0.1, y_lim_min + 0.2), feedback[0], feedback[1], color='blue',
                          alpha=0.1, label='feedback' if i == 0 else '')
        ax1.text(feedback[0] + feedback_length / 2, y_lim_min + 0.15, f'{feedback[2]}', va='center', ha='center',
                 fontweight='bold')

plt.xlabel('Attempts')
ax1.set_ylabel('Error angles (rad)')

# plot 0 line
ax1.axhline(0, color='black', linewidth=0.7)

# combine and print legend
handles_1, labels_1 = ax1.get_legend_handles_labels()
if ax2:
    handles_2, labels_2 = ax2.get_legend_handles_labels()
    handles = handles_1 + handles_2
    labels = labels_1 + labels_2
else:
    handles = handles_1
    labels = labels_1
ax1.legend(handles, labels, loc='center left', bbox_to_anchor=(1.05, 0.5))
plt.subplots_adjust(right=0.85, left=0.05)
subject_id = subject_id(path)
script_name = script_name(path)
plt.title(f'Error angles and experimental conditions for subject {subject_id} in the {script_name} experiment')
plt.savefig(f'{path}/experiment.png')  # Save the plot
plt.show()
