import importlib
import math
import os
import random
import sys
from datetime import datetime, date
from tkinter import *

import numpy as np
import pandas as pd
import pygame
from screeninfo import get_monitors

import GUI

"""
This program is a Python-based experimental setup, suitable for neuromotor study, namely, motor learning and motor adaptation. 
The program incorporates a reaching game where participants are tasked with moving a cursor to a target. 
This setup is designed to test various conditions, such as motor noise and perturbation effects (similar to prism adaptation),
on participants' performance
In different phases of the experiment, the cursor movement can be perturbed by a certain angle or by adding noise, mimicking cerebellar dysfunction,
or changing the target position.
Additionally, the program can provide feedback to the participants in the form of a trajectory, end position, or reinforcement 
in order to study motor learning and adaptation processes in these conditions.
The program is designed to be flexible and easy to use, with the possibility to change the experimental setup and parameters.
The program is divided into two main parts: the main program and the experimental setup scripts.
The main program is responsible for running the game loop, handling events, and saving the data.
The experimental setup scripts contain the parameters for the game loop, such as motor noise, perturbation mode, feedback mode, etc.
The main program imports the experimental setup script and runs the game loop according to the parameters specified in the script.
The user can choose the experimental setup and participant ID via the GUI.
The data is saved in a CSV file in the specified directory.
The program is designed to be easily extendable by adding new experimental setups and parameters to the setup scripts.
The program is written in Python using the Pygame library for graphics and GUI.
"""

### FOR USER INPUT ###
"""
Here user can specify screen resolution if needed. Otherwise the resolution will be set automatically 
"""

primary_monitor = get_monitors()[0]
resolution = (primary_monitor.width, primary_monitor.height)

user_screen = resolution

# date and time
time_now = datetime.now().strftime("%H_%M_%S")
date = date.today().strftime("%Y_%m_%d")
time_ID = f'{date}_{time_now}'

### EXPERIMENTAL SETUP ###
"""
Experimental setup for the reaching game. The setup is chosen by importing the corresponding script.
Scripts are separate files, each containing the running parameters for a specific experimental setup, 
e.g. perturbation regimes, feedback modes, motor noise, etc. Script names can be found in the 'setups_list' list.
Make sure that the scripts are located in the same directory as the main program.
Instructions for the scripts are provided in the comments at the beginning of each script.
The user can also choose to run the game in test mode.
The participant ID is entered by the user and the file saving path is generated accordingly, adding date and time values
in order to make the path unique.
"""

dialog_window = Tk()
exp_setup, participant_number, file_saving_root, mode = GUI.main_menu(dialog_window)
print('scripted exp_setup=', exp_setup)
dialog_window.mainloop()

print(exp_setup)
print(participant_number)

# Import the chosen script
# script_name = f'{setups_list[exp_setup - 1]}_script'
script = importlib.import_module(exp_setup)
print('experiment setup:', exp_setup)
print('imported script:', str(script))

# choose to run the game in test mode
# test_mode = str(input('Choose test_mode: True or False: '))
test_mode = True if mode == 'Test' else False

print('test mode:', test_mode)

# Enter Participant ID
# participant_number = str(input('enter participant ID: '))
participant_trial_folder = participant_number + '_' + time_ID  # generate unique folder for each trial of the participant
print('participant ID:', participant_number)

### FILE SAVING PATH ###
"""
File saving directory is created according to the generated participant ID and the experimental setup.
"""
# Create a folder for participant

file_saving_path = f'{file_saving_root}/{participant_number}/{participant_trial_folder}/{exp_setup}'
if test_mode:
    file_saving_path = f'{file_saving_root}/{participant_number}/{participant_trial_folder}/{exp_setup}/test/'
os.makedirs(file_saving_path, exist_ok=True)
print(file_saving_path)

### GAME SETUP ###
# Game parameters
big_screen = 2560, 1440
small_screen = 1680, 1050

SCREEN_X, SCREEN_Y = user_screen  # your screen resolution
WIDTH, HEIGHT = SCREEN_X // 1, SCREEN_Y // 1  # be aware of monitor scaling on windows (150%)
CIRCLE_SIZE = 40
TARGET_SIZE = CIRCLE_SIZE
TARGET_RADIUS = 300
ATTEMPTS_LIMIT = 400
START_POSITION = (WIDTH // 2, HEIGHT // 2)
START_ANGLE = 0
TIME_LIMIT = 1000  # time limit in ms
OUTER_RADIUS = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

target_color = BLUE
center_color = WHITE

# Initialize Pygame
pygame.init()

# Set up the display
if test_mode:
    screen = pygame.display.set_mode((WIDTH - 200, HEIGHT - 200))
else:
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Reaching Game")

# Initialize game metrics
clock = pygame.time.Clock()
escape = False

# parameters that change according to the active script and their defaults
parameters = {
    'running': True,
    'motor_noise': 0,
    'target_mode': 'fix',
    'sequence_target': 0,
    'perturbation_mode': False,
    'MASK_RADIUS': 0.75 * TARGET_RADIUS,
    'max_perturbation': -30,

    # feedback mode
    'feedback': False,

    # assisting modes
    'assisting_circle': False,
    'assisting_flicker': False,
    'limited_mask': False,
}

default_parameters = parameters.copy()

# dynamic variables used for calculations inside the game loop
dynamic_variables = {
    'motor_noise_perturbation': 0.0,
    'gradual_step': 0,
    'gradual_attempts': 1,
    'total_perturbation': 0,
    'perturbation_angle': 0,
    'circle_pos': [0.0, 0.0],
    'game_event': None,
    'score': 0,
    'attempts': 0,
    'error_angle': 0,
    'move_faster': False,
    'hit_time': 0,
    'start_time': 0,
    'target': None,
    'trajectory': [(0, 0)],
    'attempt_trajectory': [(0, 0)],
}

# data to be saved
data = {'attempts': [],
        'error_angle': [],
        'move_faster': [],

        'perturbation_mode': [],
        'total_perturbation': [],

        'motor_noise': [],
        'MASK_RADIUS': [],
        'sequence_target': [],

        'max_perturbation': [],
        'feedback': []
        }

# update parameters according to the script presets
parameters = {k: script.return_parameters()[k] if k in script.return_parameters() else default_parameters[k] for k in
              parameters}


### FUNCTIONS TO CHECK GAME STATES ###

# Function to generate coordinates for the target position
def generate_target_position():
    """Function to generate coordinates for the target position depending on the target_mode in effect
    Returns:
         [x, y] coordinates for the target position
    """
    angle = 0
    if parameters['target_mode'] == 'random':
        angle = random.uniform(0, 2 * math.pi)  # random angle for each attempt

    elif parameters['target_mode'] == 'fix':
        angle = math.radians(START_ANGLE)  # fix the target at a specific angle for all attempts

    elif parameters['target_mode'] == 'sequence':
        angle = math.radians(
            parameters['sequence_target'])  # sequence_target is a variable that changes over the attempts

    target_x = WIDTH // 2 + TARGET_RADIUS * math.sin(angle)
    target_y = HEIGHT // 2 + TARGET_RADIUS * -math.cos(angle)  # zero-angle at the top
    return [target_x, target_y]


# Function to check if the current target is reached
def check_target_reached():
    """
    Function to check if the current target is reached.
    First, it checks if there is a target. Then, it calculates the distance
    between the circle and the target and returns True if the distance is less
    than or equal to half the circle's size.

    Returns:
         bool: True if the target is within the circle, False otherwise.
    """
    if dynamic_variables['target']:
        distance = math.hypot(float(dynamic_variables['circle_pos'][0]) - dynamic_variables['target'][0],
                              float(dynamic_variables['circle_pos'][1]) - dynamic_variables['target'][1])
        if distance <= CIRCLE_SIZE // 2:
            return True
    return False


# Function to check if player has returned to the starting position
def at_start_position():
    """
    Function to check if the starting position is reached.
    First, it calculates the distance between the mouse position and the starting position
    and returns True if the distance is less than or equal to the circle's size

    Returns:
         bool: True if the mouse position is within the circle, False otherwise.
    """
    distance = math.hypot(mouse_pos[0] - START_POSITION[0], mouse_pos[1] - START_POSITION[1])
    if distance <= CIRCLE_SIZE:
        return True
    return False


def get_mouse_angle():
    """ Function to calculate the angle between the mouse position and the starting position
    Returns:
            float: angle in radians
    """
    deltax = pygame.mouse.get_pos()[0] - START_POSITION[0]
    deltay = pygame.mouse.get_pos()[1] - START_POSITION[1]
    mouse_angle = math.atan2(deltay, deltax)  # mouse angle in RADIANS
    return mouse_angle


def mouse_distance():
    """ Function to calculate the distance between the mouse position and the starting position
    Returns:
            float: distance
    """
    deltax = pygame.mouse.get_pos()[0] - START_POSITION[0]
    deltay = pygame.mouse.get_pos()[1] - START_POSITION[1]
    distance = math.hypot(deltax, deltay)
    return distance


def movement_parameters():
    """ Function to calculate the cursor movement parameters
    Updates the following parameters based on the current game state:
            circle_pos: [x,y] coordinates for the cursor position relative to the mouse position given perturbation
            gradual_step: int, current step for gradual perturbation
            gradual_attempts: int, passed number of attempts for gradual perturbation
            total_perturbation: float, the total perturbation angle in radians
            perturbation_angle: float, the perturbation angle in radians
    """

    # calculate perturbation parameters

    # sudden perturbation
    if parameters['perturbation_mode'] == 'sudden':
        dynamic_variables['perturbation_angle'] = parameters['max_perturbation']

    # gradual perturbation
    if parameters['perturbation_mode'] == 'gradual':
        if not dynamic_variables['target'] and at_start_position():
            dynamic_variables['gradual_attempts'] += 1
        dynamic_variables['gradual_step'] = np.min([np.ceil(dynamic_variables['gradual_attempts'] / 3), 10])
        dynamic_variables['perturbation_angle'] = dynamic_variables['gradual_step'] * parameters[
            'max_perturbation'] / 10
    # random perturbation
    if parameters['perturbation_mode'] == 'random':
        if not dynamic_variables['target'] and at_start_position():
            dynamic_variables['perturbation_angle'] = np.degrees(random.uniform(-math.pi / 4, +math.pi / 4))

    # reset perturbation parameters if perturbation mode is off
    if parameters['perturbation_mode'] == False:
        dynamic_variables['perturbation_angle'] = 0
        dynamic_variables['gradual_step'] = 0
        dynamic_variables['gradual_attempts'] = 1

    # generate motor noise
    generate_motor_noise()

    # calculate the total perturbation and resulting cursor movement parameters
    dynamic_variables['total_perturbation'] = np.radians(dynamic_variables['perturbation_angle']) + np.radians(
        dynamic_variables['motor_noise_perturbation'])
    perturbed_mouse_angle = mouse_angle - dynamic_variables['total_perturbation']
    perturbed_mouse_pos = [
        START_POSITION[0] + distance * math.cos(perturbed_mouse_angle),
        START_POSITION[1] + distance * math.sin(perturbed_mouse_angle)]
    dynamic_variables['circle_pos'] = perturbed_mouse_pos  # calculate the cursor position


def get_error_angle():
    """ Function to calculate the error angle between the target and the circle end position
    Returns:
            float: error_angle in radians
    """
    target_angle = math.atan2(dynamic_variables['target'][1] - START_POSITION[1],
                              dynamic_variables['target'][0] - START_POSITION[0])
    circle_end_angle = math.atan2(float(dynamic_variables['circle_pos'][1]) - START_POSITION[1],
                                  float(dynamic_variables['circle_pos'][0]) - START_POSITION[0])
    error_angle = circle_end_angle - target_angle
    error_angle = (error_angle + math.pi) % (2 * math.pi) - math.pi  # wrap to -pi to pi
    return error_angle


def write_data():
    """ Function to write the data to data dictionary according to its keys from parameters or dynamic_variables

    """
    for key in data:
        data[key].append(parameters[key]) if key in parameters else data[key].append(dynamic_variables[key])


def generate_motor_noise():
    """ Function to generate motor noise perturbation value
    Returns:
            float: motor_noise_perturbation
    """

    if not dynamic_variables['target'] and at_start_position():
        if parameters['motor_noise'] != 0.0:
            while True:
                dynamic_variables['motor_noise_perturbation'] = float(np.random.normal(0, parameters['motor_noise']))
                if abs(dynamic_variables['motor_noise_perturbation']) <= 10:
                    break
            return dynamic_variables['motor_noise_perturbation']
        else:
            dynamic_variables['motor_noise_perturbation'] = 0.0
            return dynamic_variables['motor_noise_perturbation']


def draw_trajectory():
    """
    Function to draw the trajectory of the cursor
    """
    for coordinate in dynamic_variables['attempt_trajectory']:
        pygame.draw.circle(screen, WHITE, coordinate, 2)


def draw_end_pos():
    """
    Function to draw the end position of the cursor
    """
    pygame.draw.circle(screen, RED, np.array(dynamic_variables['attempt_trajectory'][-1]), 10)

def screenshot():
    """
    Function to take a screenshot of the game window
    """

    pygame.image.save(screen, f'{file_saving_path}/f{dynamic_variables['attempts']}_screenshot.png')

### MAIN GAME LOOP ###

while parameters['running']:
    screen.fill(BLACK)

    # Hide the mouse cursor
    pygame.mouse.set_visible(False)



    # update game parameters according to the script
    script.update_parameters(dynamic_variables['attempts'], dynamic_variables['game_event'])
    parameters = {k: script.return_parameters()[k] if k in script.return_parameters() else default_parameters[k] for k
                  in
                  parameters}

    # Quit the game if escape is pressed
    if escape == True:
        parameters['running'] = False

    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()

    # calculate mouse_distance and mouse_angle
    distance = mouse_distance()
    mouse_angle = get_mouse_angle()

    # get circle movement parameters
    movement_parameters()

    # save the trajectory of the cursor
    if dynamic_variables['target']:
        dynamic_variables['trajectory'].append(dynamic_variables['circle_pos'])

    ### HIT ###

    # hit if circle touches target's center
    if check_target_reached():

        # get hit time, used later for assist in return to start position
        dynamic_variables['hit_time'] = pygame.time.get_ticks()

        # paint the center green if there was a hit for 'reinforcement feedback' mode
        if parameters['feedback'] == 'reinforcement':
            center_color = GREEN

        # update game metrics
        dynamic_variables['score'] += 1
        dynamic_variables['attempts'] += 1

        # calculate and save error angles between target and circle end position for a hit
        dynamic_variables['error_angle'] = get_error_angle()
        write_data()

        # Disable target after hit
        dynamic_variables['target'] = None

        # Reset attempt time after hitting the target
        dynamic_variables['start_time'] = 0

        # save the trajectory of the cursor for the attempt and reset the trajectory for the next attempt
        dynamic_variables['attempt_trajectory'] = dynamic_variables['trajectory']
        dynamic_variables['trajectory'] = []

    ### MISS ###

    # miss if player leaves the target_radius + 1% tolerance
    elif dynamic_variables['target'] and math.hypot(float(dynamic_variables['circle_pos'][0]) - START_POSITION[0],
                                                    float(dynamic_variables['circle_pos'][1]) - START_POSITION[
                                                        1]) > TARGET_RADIUS * 1.01:

        # get miss time, used later for assist in return to start position
        dynamic_variables['hit_time'] = pygame.time.get_ticks()

        # update game metrics
        dynamic_variables['attempts'] += 1

        # Calculate and save errors between target and circle end position for a miss
        dynamic_variables['error_angle'] = get_error_angle()

        # reinforcement feedback mode
        if parameters['feedback'] == 'reinforcement':  # paint the center red if there was a miss
            center_color = RED
            if abs(np.degrees(
                    dynamic_variables[
                        'error_angle'])) < 8.5:  # paint the circle in Yellow for intermediate reinforcement if the angle is less than 8.5 degrees
                center_color = YELLOW
                dynamic_variables['score'] += 0.25

        # exclude attempts where the cursor wandered away in the opposite direction in the dark
        if abs(np.degrees(
                dynamic_variables['error_angle'])) > 100:
            dynamic_variables['attempts'] -= 1

        # error_angles.append(error_angle)
        write_data()

        # Set target to None to indicate miss
        dynamic_variables['target'] = None

        # Reset start_time after missing the target
        dynamic_variables['start_time'] = 0

        # save the trajectory of the cursor for the attempt and reset the trajectory for the next attempt
        dynamic_variables['attempt_trajectory'] = dynamic_variables['trajectory']
        dynamic_variables['trajectory'] = []

    # Other feedback modes
    draw_trajectory() if parameters[
                             'feedback'] == 'trajectory' else None  # draw the trajectory if trajectory mode is on
    draw_end_pos() if parameters[
                          'feedback'] == 'end_pos' else None  # draw the end position if end_pos mode is on

    if not parameters['feedback']:  # paint the center white if there is no feedback mode
        center_color = WHITE

    # teleport the cursor to the center at the vicinity of the center
    if not dynamic_variables['target'] and distance < 80:
        pygame.mouse.set_pos(START_POSITION)

    # Check if player moved to the center and generate new target
    if not dynamic_variables['target'] and at_start_position():
        dynamic_variables['target'] = generate_target_position()  # get coordinates for the new target
        dynamic_variables['move_faster'] = False
        dynamic_variables['start_time'] = pygame.time.get_ticks()  # Start the timer for the attempt
        perturbation_rand = random.uniform(-math.pi / 4,
                                           +math.pi / 4)  # generate new random perturbation for type 'random'

    # Check if time limit for the attempt is reached
    current_time = pygame.time.get_ticks()
    if dynamic_variables['start_time'] != 0 and (current_time - dynamic_variables['start_time']) > TIME_LIMIT:
        dynamic_variables['move_faster'] = True
        dynamic_variables['start_time'] = 0  # Reset start_time

    # Show 'MOVE FASTER!'
    if dynamic_variables['move_faster']:
        font = pygame.font.Font(None, 36)
        text = font.render('MOVE FASTER!', True, RED)
        text_rect = text.get_rect(center=START_POSITION)
        screen.blit(text, text_rect)

    ### GENERATE PLAYING FIELD ###
    # Draw current target
    if dynamic_variables['target']:
        pygame.draw.circle(screen, target_color, dynamic_variables['target'],
                           TARGET_SIZE // 2)  # draw the target if the coordinates are available (i.e., if target is not None)

    # Draw start position
    pygame.draw.circle(screen, center_color, START_POSITION, 10)  # draw the center

    # Draw cursor
    if distance <= parameters['MASK_RADIUS']:
        pygame.draw.circle(screen, WHITE, dynamic_variables['circle_pos'], CIRCLE_SIZE // 2)  # draw the cursor

    ### ASSISTANCE ###
    # Draw assisting circle if returning to start position takes too long

    if parameters['assisting_circle']:
        if not dynamic_variables['target'] and pygame.time.get_ticks() - dynamic_variables['hit_time'] > 5000:
            pygame.draw.circle(screen, WHITE, START_POSITION, radius=distance, width=1)

    # implement assisting flickering cursor if returning to start position takes too long
    if parameters['assisting_flicker']:
        if not dynamic_variables['target'] and pygame.time.get_ticks() - dynamic_variables['hit_time'] > 5000:
            if 0 < np.sin(pygame.time.get_ticks() / 750) < 0.5:
                pygame.draw.circle(screen, YELLOW, dynamic_variables['circle_pos'], CIRCLE_SIZE // 4)

    # limit mask radius
    if parameters['limited_mask']:
        if distance > OUTER_RADIUS:
            pygame.draw.circle(screen, WHITE, dynamic_variables['circle_pos'], CIRCLE_SIZE // 2)

    ### DISPLAY METRICS ###
    # Show attempts
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Attempts: {dynamic_variables['attempts']}", True, WHITE)
    screen.blit(score_text, (10, 40))

    # Show score
    font = pygame.font.Font(None, 52)
    score_text = font.render(f"SCORE: {dynamic_variables['score']}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - 100, 40))

    if test_mode:
        # display the cursor
        pygame.draw.circle(screen, WHITE, dynamic_variables['circle_pos'], CIRCLE_SIZE // 2)

        # Show score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {dynamic_variables['score']}", True, WHITE)
        screen.blit(score_text, (10, 10), )

        # Show Mouse_angle
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Mouse_Ang: {np.rint(np.degrees(mouse_angle))}", True, WHITE)
        screen.blit(score_text, (10, 70))

        # Show total_perturbation

        font = pygame.font.Font(None, 36)
        value = np.degrees(dynamic_variables['total_perturbation'])
        formatted_value = "{:.2f}".format(value)
        score_text = font.render(f"Total_perturbation: {formatted_value}", True,
                                 WHITE)
        screen.blit(score_text, (10, 100))

        # Show gradual_step
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Grad_step: {dynamic_variables['gradual_step']}", True, WHITE)
        screen.blit(score_text, (10, 130))

        # Show if perturbation_mode is on or off
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Perturbation: {parameters['perturbation_mode']}", True, WHITE)
        screen.blit(score_text, (10, 160))

        # show perturbation_angle
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"perturbation angle: {dynamic_variables['perturbation_angle']}", True, WHITE)
        screen.blit(score_text, (10, 190))

        # show motor_noise_perturbation
        font = pygame.font.Font(None, 36)
        formatted_motor_noise_perturbation = "{:.2f}".format(dynamic_variables['motor_noise_perturbation'])
        score_text = font.render(f"motor noise: {formatted_motor_noise_perturbation}", True, WHITE)
        screen.blit(score_text, (10, 220))

        # show motor_noise_perturbation
        font = pygame.font.Font(None, 36)
        formatted_error_angle = "{:.2f}".format(np.degrees(dynamic_variables['error_angle']))
        score_text = font.render(f"error_angle: {formatted_error_angle}", True, WHITE)
        screen.blit(score_text, (10, 250))

        # Show target_angle
        font = pygame.font.Font(None, 36)
        formatted_target_angle = "{:.2f}".format((parameters['sequence_target']))
        score_text = font.render(f"target_angle: {formatted_target_angle}", True, WHITE)
        screen.blit(score_text, (10, 280))

        # Show circle_pos
        font = pygame.font.Font(None, 36)
        formatted_circle_pos_x = "{:.2f}".format(float(dynamic_variables['circle_pos'][0]))
        formatted_circle_pos_y = "{:.2f}".format(float(dynamic_variables['circle_pos'][1]))
        score_text = font.render(f"circle_pos: {formatted_circle_pos_x},{formatted_circle_pos_y}", True, WHITE)
        screen.blit(score_text, (10, 310))

        # Show target_pos
        font = pygame.font.Font(None, 36)
        if dynamic_variables['target']:
            formatted_target_pos_x = "{:.2f}".format(dynamic_variables['target'][0])
            formatted_target_pos_y = "{:.2f}".format(dynamic_variables['target'][1])
            score_text = font.render(f"target_pos: {formatted_target_pos_x},{formatted_target_pos_y}", True, WHITE)
            screen.blit(score_text, (10, 340))

        # Show gradual_attempts
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Grad_attempts: {dynamic_variables['gradual_attempts']}", True, WHITE)
        screen.blit(score_text, (10, 370))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            dynamic_variables['game_event'] = 'escape'
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Press 'esc' to close the experiment
                dynamic_variables['game_event'] = 'escape'
                escape = True

                # Change script_parameters manually
            elif event.key == pygame.K_4:  # Press '4' to start perturbation_mode
                dynamic_variables['game_event'] = 'test_perturbation'
            elif event.key == pygame.K_5:  # Press '5' to end perturbation_mode
                dynamic_variables['game_event'] = 'end perturbation'
            elif event.key == pygame.K_6:  # Press '6' to set the mask radius to 400
                dynamic_variables['game_event'] = 'mask400'
            elif event.key == pygame.K_s:  # press 's' for a screenshot
                screenshot()
            elif event.key == pygame.K_m:
                pygame.mouse.set_visible(True) if pygame.mouse.get_visible() == False else pygame.mouse.set_visible(
                    False)


    # Update display
    pygame.display.flip()
    clock.tick(60)

print('game finished without issues')
# Quit Pygame
pygame.quit()

### SAVING IMPORTANT DATA ###

# save error_angles in a csv file as rows

df = pd.DataFrame(data)
df.to_csv(f'{file_saving_path}/experimental_data.csv', index=False)

sys.exit()
