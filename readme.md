# ComfyUI API Streamlit Client Example

This repository contains a simple example code demonstrating how to use the ComfyUI API from a Streamlit client.

## Demo

YouTube link: https://youtu.be/Ll5slBLa0II

## Setup and Run

1. Set up a Python 3.10 virtual environment on Anaconda:
   ```bash
   conda create -n comfyapi python3.10 -y
   conda activate comfyapi
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```bash
   streamlit run main.py -- --server_address=[comfyui server ip]:[comfyui port]
   ```

## Notes

- Ensure Python 3.10 is installed on your system.
- Adjust the `--server_address` parameter if your ComfyUI server runs on a different address.
- Make sure your ComfyUI server is running and accessible before starting the Streamlit application.

