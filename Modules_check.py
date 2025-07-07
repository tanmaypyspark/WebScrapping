import subprocess
import importlib.util
import os
import json
import pkg_resources
# from wrapperWebScrap import getConfig

def getConfig(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

os.getcwd()

def get_pip_path():
    """
    Returns the path to the pip executable in the clean_env virtual environment.
    """
    base_path = os.getcwd()
    venv_path = os.path.join(base_path,"clean_env", "Scripts", "pip.exe")
    if os.path.exists(venv_path):
        return venv_path
    else:
        return "pip"  # Fallback to the default pip if clean_env is not found

def is_module_installed(module_name):
    """
    Checks if a Python module is installed, including version-specific checks.

    Args:
        module_name: The name of the module (string), optionally with a version (e.g., 'googletrans==3.1.0a0').

    Returns:
        True if the module is installed, False otherwise.
    """
    try:
        # Check if a specific version is required
        pkg_resources.require(module_name)
        return True
    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
        return False

def install_missing_modules(modules):
    """
    Installs missing Python modules using pip.

    Args:
        modules: A list of module names (strings).
    """
    pip_path = get_pip_path()
    for module in modules:
        print(f"Checking if {module} is installed...")
        if not is_module_installed(module):
            print(f"Installing {module}...")
            try:
                subprocess.check_call([pip_path, "install", module])
                print(f"{module} installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {module}: {e}")

def upgrade_modules(modules):
    """
    Upgrades specified Python modules using pip.

    Args:
        modules: A list of module names (strings).
    """
    pip_path = get_pip_path()
    for module in modules:
        print(f"Upgrading {module}...")
        try:
            subprocess.check_call([pip_path, "install", "--upgrade", module])
            print(f"{module} upgraded successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error upgrading {module}: {e}")

# def is_module_installed(module_name):
#   """
#   Checks if a Python module is installed.

#   Args:
#       module_name: The name of the module (string).

#   Returns:
#       True if the module is installed, False otherwise.
#   """
#   return importlib.util.find_spec(module_name) is not None

def check_module_installation_path(module_name):
    """
    Prints the installation path of a specific module.

    Args:
        module_name: The name of the module (string).
    """
    try:
        module = importlib.import_module(module_name)
        print(f"{module_name} is installed at: {module.__file__}")
    except ImportError:
        print(f"{module_name} is not installed.")

def dynamic_import(modules):
    """
    Dynamically imports modules from a list.

    Args:
        modules: A list of module names (strings).

    Returns:
        A dictionary with module names as keys and imported modules as values.
    """
    imported_modules = {}
    for module_name in modules:
        try:
            imported_modules[module_name] = importlib.import_module(module_name)
            print(f"Successfully imported {module_name}")
        except ImportError as e:
            print(f"Error importing {module_name}: {e}")
    return imported_modules

def preSetupCheck():
    # Example usage:
    config_path = r'Config\config.json'
    config = getConfig(config_path)
    
    package = config["Modules"]
    required_modules = package["required_modules"] #beautifuolsoup4 is the correct name.
    install_missing_modules(required_modules)
    # Modules to upgrade
    modules_to_upgrade = package["modules_to_upgrade"]  # Add other modules here if needed
    upgrade_modules(modules_to_upgrade)
    # Now, you can safely import and use the modules in your main script:
    try:
        # Dynamically import modules
        imported_modules = dynamic_import(required_modules + modules_to_upgrade)
        # import pandas
        # import selenium
        # from bs4 import BeautifulSoup
        # import logging
        # import 

        print("All modules are available.")
        # Your main script logic here...
        for module in required_modules:
            check_module_installation_path(module)
        return True

    except ImportError as e:
        print(f"Module import error after installation: {e}")
        return False
# preSetupCheck()