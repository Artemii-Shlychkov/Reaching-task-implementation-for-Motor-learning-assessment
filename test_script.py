# Script for the feedback experiment

"""
This is a short TEST script in which all the possible regimes are activated for a short number of attempts and can be tested

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

    REINFORCEMENT:
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

script_parameters = {
    'running': True,
    'motor_noise': 0,
    'target_mode': 'sequence',
    'sequence_target': 0,
    'perturbation_mode': False,
    'assisting_circle': True,
    'max_perturbation': 30,
    'feedback': False
}

def update_parameters(attempts,event):

    # target angles
    if attempts == 0:
        script_parameters['sequence_target'] = 60
    elif attempts == 25:
        script_parameters['sequence_target'] = 105
    elif attempts == 50:
        script_parameters['sequence_target'] = -100
    elif attempts == 75:
        script_parameters['sequence_target'] = -15

    #motor noise

    if attempts == 50:
        script_parameters['motor_noise'] = 2
    elif attempts == 50:
        script_parameters['motor_noise'] = 5
    elif attempts == 80:
        script_parameters['motor_noise'] = 10

    # perturbation type and mode
    if attempts == 10:
        script_parameters['perturbation_mode'] = 'sudden'
    elif attempts == 20:
        script_parameters['perturbation_mode'] = False
    elif attempts == 30:
        script_parameters['perturbation_mode'] = 'gradual'
    elif attempts == 40:
        script_parameters['perturbation_mode'] = False
    elif attempts == 50:
        script_parameters['perturbation_mode'] = 'random'
    elif attempts == 60:
        script_parameters['perturbation_mode'] = False
    elif attempts == 70:
        script_parameters['perturbation_mode'] = 'gradual'
    elif attempts == 80:
        script_parameters['perturbation_mode'] = False
    elif attempts == 90:
        script_parameters['perturbation_mode'] = 'sudden'
        script_parameters['max_perturbation'] = 15
    # feedback modes

    if   attempts == 1:
        script_parameters['feedback'] = 'trajectory'
    elif attempts == 2:
        script_parameters['feedback'] = False

    elif attempts == 3:
        script_parameters['feedback'] = 'reinforcement'
    elif attempts == 6:
        script_parameters['feedback'] = False
    elif attempts == 7:
        script_parameters['feedback'] = 'end_pos'
    elif attempts == 9:
        script_parameters['feedback'] = False

    # end the experiment
    if attempts == 100:
        script_parameters['running'] = False

    # mask
    if attempts == 1:
        script_parameters["MASK_RADIUS"] = 0
    if attempts == 600:
        script_parameters["MASK_RADIUS"] = 400

    # events (manual interventions via keyboard)
    if event == 'escape':
        script_parameters['running'] = False
    if event == 'test_perturbation':
        script_parameters['perturbation_mode'] = True
        script_parameters['perturbation_type'] = 'sudden'
    if event == 'end perturbation':
        script_parameters['perturbation_mode'] = False
    if event == 'mask400':
        script_parameters["MASK_RADIUS"] = 400

    return script_parameters

def return_parameters():
    return script_parameters