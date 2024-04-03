# Script for the baseline experiment

"""
The script contains the parameters for the inference experiment.
The parameters are updated after a certain number of attempts.
Only parameters listed in parameters dictionary are changed in the main program.
Other parameters of the main program will remain default
The full list of possible parameters:
    running: bool, True if the experiment is running, set to False to end the experiment
    motor_noise: int, the std. dev. of normal random distribution to generate motor noise perturbation, mean is 0
    target_mode: str, 'sequence', 'random' or 'fix', the mode of target presentation:
        sequence - set explicit values of target angles in sequence_target parameter,
        random - random angle for each trial,
        fix - 0 degrees for each attempt
    sequence_target: int, the explicit target angle for the sequence mode
    perturbation_mode: bool, True if the perturbation is active
    perturbation_type: str, 'gradual', 'sudden' or 'random', the type of perturbation:
        gradual - gradually increasing perturbation in 10 steps after every 3 attempts until 'max_perturbation',
        sudden - fixed perturbation of 'max_perturbation' degree,
        random - random perturbation for each attempt (from -pi/4 to pi/4)
    max_perturbation: int, the maximum perturbation angle for the sudden perturbation type. Use positive values for
        counter-clockwise perturbation and negative values for clockwise perturbation
    MASK_RADIUS: int, the radius of the area where the cursor is visible, set to 0 to hide the cursor entirely

    REINFORCEMENT:
    reinforcement_feedback: bool, True if the reinforcement feedback is active
    end_pos_feedback: bool, True if the end position feedback is active
    trajectory_feedback: bool, True if the trajectory feedback is active

    ASSISTANCE:
    assisting_circle: bool, True if the assisting circle is active
    assisting_flicker: bool, True if the assisting flickering cursor is active
    limited_mask: bool, True if the cursor shall be visible beyond some distance from the center

    EVENTS (needed for interventions via keyboard):
    escape: bool, True if the escape key was pressed, quits the game
    test_perturbation: bool, True if 4 key was pressed, starts the sudden perturbation regime
    end perturbation: bool, True if 5 key was pressed, ends the sudden perturbation regime
    mask400: bool, True if 6 key was pressed, sets the mask radius to 400 (makes cursor visible)

Necessary parameters can be straightforwardly added to the dictionary within the update_parameters function.
Any parameters can be deleted from the dictionary within the update_parameters function, default values will be then
restored and used in the main program.
"""


script_parameters = {
    'running': True,
    'motor_noise': 0,
    'target_mode': 'sequence',
    'sequence_target': 0,
    'perturbation_mode': False,
    'perturbation_type': 'sudden',
    'reinforcement_feedback': False,
    'trajectory_feedback': False,
    'end_pos_feedback': False,
    'assisting_circle': False,
    'max_perturbation': 30, #counter clockwise
}


def update_parameters(attempts,event):
    # perturbation
    if attempts == 20:
        script_parameters['perturbation_mode'] = True
        script_parameters['perturbation_type'] = 'sudden'
    elif attempts == 80:
        script_parameters['perturbation_mode'] = False
    elif attempts == 120:
        script_parameters['perturbation_mode'] = True
        script_parameters['perturbation_type'] = 'gradual'
    elif attempts == 180:
        script_parameters['perturbation_mode'] = False
    # end of the experiment
    elif attempts == 200:
        script_parameters['running'] = False

    # event handling (manual interventions via keyboard)
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
