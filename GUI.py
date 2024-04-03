"""
This script is responsible for creating the GUI for the experimental setup.
It allows the user to choose the experimental setup, subject ID, root folder and game mode.
The user can choose between the following experimental setups: Motor noise, Feedback, Interference, Baseline and Test.
The user can choose between two game modes: Test and Full screen.
The user can choose the root folder for the experiment.
The user can enter the subject ID.
The user can start the experiment by clicking the GO button.
The user can choose the csv file with the experiment results.
The user can start the data analysis by clicking the GO button.
"""

from tkinter import *
from tkinter import ttk


def main_menu(root):
    """
    This function creates the main menu for the experimental setup.
    Args:
        root: Tk() object
    Returns:
        exp_setup: str, the chosen experimental setup
        id: str, the subject ID
        path: str, the root folder for the experiment
        mode: str, the chosen game mode
    """
    root.title("Experimental Setup")
    setups_dict = {'Motor noise': 'motor_noise_script', 'Feedback': 'feedback_script',
                   'Interference': 'interference_script', 'Baseline': 'baseline_script', 'Test': 'test_script'}
    resolution = root.winfo_screenwidth(), root.winfo_screenheight()
    box_width, box_height = 400, 850
    x_pos = resolution[0] // 2 - box_width // 2
    y_pos = resolution[1] // 2 - box_height // 2

    ttk.Style().configure('TRadiobutton', font=('calibri', 20, 'bold'), borderwidth='4', padding=(20, 10))

    path = StringVar()
    mode = StringVar()
    exp_setup = StringVar()
    subject_id = StringVar()

    root.geometry(f"{box_width}x{box_height}+{x_pos}+{y_pos}")
    root.columnconfigure(0, weight=1)
    Label(root, text='Enter Subject ID:', font=('calibri', 24, 'bold')).grid(column=0, row=0, pady=10)
    Entry(root, font=('calibri', 24, 'bold'), textvariable=subject_id).grid(column=0, row=1, pady=10)
    Label(root, text='Choose experimental setup:', font=('calibri', 24, 'bold')).grid(column=0, row=2, pady=10)

    def choose_file_path(path):
        """
        This function allows the user to choose the root folder for the experiment.
        Args:
            path: StringVar object
        Returns:
            None
        """

        from tkinter import filedialog
        filepath = filedialog.askdirectory()
        Label(root, text=filepath, font=('calibri', 12, 'bold')).grid(column=0, row=len(setups_dict) + 4, pady=10)
        print(filepath)
        path.set(filepath)

    for i, setup in enumerate(setups_dict.keys()):
        ttk.Radiobutton(root, text=setup, value=setups_dict[setup], variable=exp_setup).grid(column=0, row=i + 3,
                                                                                             padx=10, pady=2,
                                                                                             sticky='ew')

    file_saving_path = Button(root, text="Choose root folder \nfor your experiment",
                              command=lambda: choose_file_path(path), width=20, height=2, font=('calibri', 18, 'bold'),
                              borderwidth='4', relief='raised')
    file_saving_path.grid(column=0, row=len(setups_dict) + 3, columnspan=1, padx=10, pady=10)

    select_button = Button(root, text="GO", command=lambda: root.destroy(), width=10, height=2,
                           font=('calibri', 18, 'bold'), borderwidth='4', relief='raised')
    select_button.grid(column=0, row=len(setups_dict) + 8, columnspan=1, padx=10, pady=10)

    Label(root, text='Choose Game mode:', font=('calibri', 24, 'bold')).grid(column=0, row=len(setups_dict) + 5,
                                                                             pady=10)
    ttk.Radiobutton(root, text='Test', value='Test', variable=mode).grid(column=0, row=len(setups_dict) + 6, padx=10,
                                                                         pady=2, sticky='ew')
    ttk.Radiobutton(root, text='Full screen', value='full_screen', variable=mode).grid(column=0,
                                                                                       row=len(setups_dict) + 7,
                                                                                       padx=10, pady=2, sticky='ew')

    root.mainloop()
    path = path.get()
    exp_setup = exp_setup.get()
    id = subject_id.get()
    mode = mode.get()
    return exp_setup, id, path, mode


def reader_menu(dialog_window):
    """ This function allows the user to choose the csv file with the experiment results.
    Args:
        dialog_window: Tk() object
    Returns:
        filepath: str, the chosen csv file

    """
    dialog_window.title('Choose the csv file with exp data')
    resolution = dialog_window.winfo_screenwidth(), dialog_window.winfo_screenheight()
    box_width, box_height = 350, 200
    x_pos = resolution[0] // 2 - box_width // 2
    y_pos = resolution[1] // 2 - box_height // 2
    path = StringVar()
    dialog_window.geometry(f"{box_width}x{box_height}+{x_pos}+{y_pos}")
    dialog_window.columnconfigure(0, weight=1)
    dialog_window.columnconfigure(1, weight=1)

    def choose_file_path(path):
        from tkinter import filedialog
        filepath = filedialog.askopenfilename()
        Label(dialog_window, text=f'{(filepath.split('/')[-1])}', font=('calibri', 12, 'bold')).grid(column=1, row=1,
                                                                                                     pady=10)
        # print(filepath)
        path.set(filepath)

    Label(dialog_window, text='Chosen file:', font=('calibri', 18, 'bold')).grid(column=0, row=1, pady=10)
    file_saving_path = Button(dialog_window, text="Choose the csv file with \nyour experiment results",
                              command=lambda: choose_file_path(path), width=20, height=2, font=('calibri', 18, 'bold'),
                              borderwidth='4', relief='raised')
    file_saving_path.grid(column=0, row=0, columnspan=2, padx=10, pady=10)
    select_button = Button(dialog_window, text="GO", command=lambda: dialog_window.destroy(), width=10, height=2,
                           font=('calibri', 18, 'bold'), borderwidth='4', relief='raised')
    select_button.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

    dialog_window.mainloop()
    filepath = str(path.get())
    # print(filepath)
    return filepath


# TEST ENVIRONMENT
'''
window = Tk()
a  = reader_menu(window)
print(a)
'''
