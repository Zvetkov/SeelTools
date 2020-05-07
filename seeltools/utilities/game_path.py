import os
import winreg
from seeltools.utilities.log import logger
from seeltools.utilities.constants import FALLBACK_WORKING_DIRECTORY


def get_game_path():
    steam_install_reg_path = r"SOFTWARE\WOW6432Node\Valve\Steam"
    hklm = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    try:
        # getting Steam installation folder from Reg
        steam_install_reg_value = winreg.OpenKey(hklm, steam_install_reg_path)
        steam_install_path = winreg.QueryValueEx(steam_install_reg_value, 'InstallPath')[0]

        # game can be installed in main Steam dir or in any of the libraries specified in config
        library_folders_config = os.path.join(steam_install_path, "SteamApps", "libraryfolders.vdf")
        library_folders = [steam_install_path]

        with open(library_folders_config, 'r') as f:
            supported_library_indexes = [f'"{i}"' for i in range(1, 11)]  # list of indexes in "0", "1" etc format
            lines = f.readlines()
            for line in lines:
                for index in supported_library_indexes:
                    # finding and cleaning any library folders found
                    if index in line:
                        directory = line.split('"		"')[1].strip().strip('"')
                        library_folders.append(directory)

        if not library_folders:
            logger.info("Library folders for Steam install not found, will try to use fallback working directory")
            return FALLBACK_WORKING_DIRECTORY

        for folder in library_folders:
            # checking that game install exist for this library and that data folder exists as well
            expected_game_path = os.path.join(folder, "SteamApps", "common", "Hard Truck Apocalypse")
            if os.path.exists(expected_game_path):
                if os.path.exists(os.path.join(expected_game_path, "data")):
                    # returining first dir found for the time being, would be better to let user choose from all found
                    return expected_game_path
    except FileNotFoundError:
        logger.info("Steam install not found, will try to use fallback working directory")

    return FALLBACK_WORKING_DIRECTORY


WORKING_DIRECTORY = get_game_path()
logger.info(f"'{WORKING_DIRECTORY}': choosen as game working directory")
