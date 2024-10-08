#!/bin/bash

function setup_env() {
    # Create a new virtual environment in the 'venv' directory
    python3 -m venv max_venv

    # Activate the virtual environment
    source max_venv/bin/activate

    # Install all dependencies from requirements.txt
    pip install -r requirements.txt

    echo "Virtual environment setup complete and dependencies installed."
}

# Call the function
setup_env