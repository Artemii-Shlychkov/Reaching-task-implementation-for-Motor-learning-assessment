# Script for the motor noise experiment

"""
The script contains the parameters for the MOTOR NOISE experiment.
This experiment is designed to test the effect of motor noise on the motor learning process.
The parameters are updated after the specified number of attempts.
Only parameters listed in 'script_parameters' dictionary of this script are also changed in the main program.
Other parameters of the main program will remain default
The full list of possible parameters:
    running: bool, True if the experiment is running, set to False to end the experiment
    motor_noise: int, the std. dev. of normal random distribution to generate motor noise perturbation, mean is 0
    target_mode: str, 'sequence', 'random' or 'fix', the mode of target presentation:
        sequence - set explicit values of target angles in sequence_target parameter,
        random - random angle for each trial,
        fix - 0 degrees for each attempt
    sequence_target: int, the explicit target angle for the sequence mode

    perturbation_mode: str, 'gradual', 'sudden' or 'random', the type of perturbation:
        gradual - gradually increasing perturbation in 10 steps after every 3 attempts until 'max_perturbation',
        sudden - fixed perturbation of 'max_perturbation' degree,
        random - random perturbation for each attempt (from -pi/4 to pi/4)
        or bool, False if the perturbation is inactive
    max_perturbation: int, the maximum perturbation angle for the sudden perturbation type. Use positive values for
        counter-clockwise perturbation and negative values for clockwise perturbation
    MASK_RADIUS: int, the radius of the area where the cursor is visible, set to 0 to hide the cursor entirely

    FEEDBACK:
    feedback: str, 'reinforcement', 'trajectory' or 'end_pos' - the type of feedback

    ASSISTANCE:
    assisting_circle: bool, True if the assisting circle is active
    assisting_flicker: bool, True if the assisting flickering cursor is active
    limited_mask: bool, True if the cursor shall be visible beyond some distance from the center

    EVENTS (needed for interventions via keyboard):
    escape: bool, True if the escape key was pressed, quits the game
    test_perturbation: bool, True if 4 key was pressed, starts the sudden perturbation regime
    end perturbation: bool, True if 5 key was pressed, ends the sudden perturbation regime
    mask400: bool, True if 6 key was pressed, sets the mask radius to 400 (makes cursor visible)

Necessary parameters can be straightforwardly added to the dictionary within the update_parameters function by calling
the corresponding key of the 'script_parameters' dictionary and setting its value.
Any parameters can be deleted from the dictionary within the update_parameters function by using 'del' command
(e.g. if you don't know what MASK_RADIUS is by default), default values will be then restored and used in the main program.
"""

parameters = {
    'running': True,
    'motor_noise': 0,
    'target_mode': 'sequence',
    'sequence_target': 0,
    'perturbation_mode': False,
    'perturbation_type': 'gradual',
    'feedback': 'reinforcement',
    'MASK_RADIUS': 0, # set to 0 to hide the cursor entirely
    'assisting_circle': True,
    'max_perturbation': 30,
}

def update_parameters(attempts, event):

    # target angles
    if attempts == 0:
        parameters['sequence_target'] = 25
    elif attempts == 100:
        parameters['sequence_target'] = -80
    elif attempts == 200:
        parameters['sequence_target'] = -35
    elif attempts == 300:
        parameters['sequence_target'] = 10

    # motor noise
    if attempts == 100:
        parameters['motor_noise'] = 2
    elif attempts == 200:
        parameters['motor_noise'] = 10
    elif attempts == 300:
        parameters['motor_noise'] = 5

    # perturbation type and mode

    if attempts == 20:
        parameters['perturbation_mode'] = 'gradual'
    elif attempts == 80:
        parameters['perturbation_mode'] = False
    elif attempts == 120:
        parameters['perturbation_mode'] = 'gradual'
    elif attempts == 180:
        parameters['perturbation_mode'] = False
    elif attempts == 220:
        parameters['perturbation_mode'] = 'gradual'
    elif attempts == 280:
        parameters['perturbation_mode'] = False
    elif attempts == 320:
        parameters['perturbation_mode'] = 'gradual'
    elif attempts == 380:
        parameters['perturbation_mode'] = False

    # end the experiment
    if attempts == 400:
        parameters['running'] = False

    # events handling (manual interventions via keyboard)
    if event == 'escape':
        parameters['running'] = False
    if event == 'test_perturbation':
        parameters['perturbation_mode'] = True
        parameters['perturbation_type'] = 'sudden'
    if event == 'end perturbation':
        parameters['perturbation_mode'] = False
    if event == 'mask400':
        parameters["MASK_RADIUS"] = 400

    return parameters

def return_parameters():
    return parameters


