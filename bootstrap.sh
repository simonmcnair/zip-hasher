#!/bin/bash

# Exit if any command fails
set -e

# Step 1: Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Step 2: Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Step 3: Install the dependencies from requirements.txt
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
