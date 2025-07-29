
# ----------------------------------------------------------------------------------
# Load libraries -------------------------------------------------------------------
# ----------------------------------------------------------------------------------
import google.generativeai as genai
import os
from datetime import datetime
import pandas as pd


# Load the user-defined files -----

import config
from config import write_log, input_file_name
from PagesLib import Page_Su_test, digitizer
from PagesLib.Page_Su_test import Page

# Note: API requires an API key, saved in GEMINI_API_KEY.txt in this directory

# ----------------------------------------------------------------------------------
# -- Execution ---------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# Valid parameters check
if (config.page_window > 1 and config.png ==True):
    raise ValueError(f"Page window is {config.page_window } but .png files must be a single page!")

# Create output directory
if not os.path.exists(config.output_maindir):
    os.makedirs(config.output_maindir)
if not os.path.exists(config.output_dir):
    os.makedirs(config.output_dir)

# Log parameters used -----------------------------------------
config.log_config()

print(f"DIGITIZATION OF THE {input_file_name} LOTTERY {config.input_file_group}")
print(f"Using task prompt in {config.prompt_text_name}")
print(f"Saving output in {config.output_dir}")

# Define the model you are going to use (flash is free with 1,500 requests per day)
model_id = config.gemini_model_id

# Set the input data
filepath = config.get_directory_filepath(group=config.input_file_group, name=config.input_file_name)

# get pages to digitize
start_page, n_pages = digitizer.check_document(filepath, all_pages=config.all_pages, start_page=config.start_page, n_pages=config.n_pages)


# Create a client -----------------------------------------

# get API key
with open("GEMINI_API_KEY.txt", "r", encoding="utf-8") as file:
    api_key = file.read()
    print("Successfully loaded API key")

genai.configure(api_key=api_key)
print("Successfully loaded Gemini AI client with API key")

print("\nStarting cleanup of uploaded Gemini files...")

try:
    files = genai.list_files()
    for f in files:
        try:
            genai.delete_file(f.name)
            print(f"Deleted file: {f.name}")
        except Exception as e:
            print(f"Failed to delete file {f.name}: {e}")
    print("✅ Gemini file storage cleanup complete.")
except Exception as e:
    print(f"Error while listing or deleting Gemini files: {e}")