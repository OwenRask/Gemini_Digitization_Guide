import os
from datetime import datetime
# ----------------------------------------------------------------------------------
# SET PARAMETERS -------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# Set File Paths -------------------------------------------
# Define which pdf input to use
# Give entire path to the file; expecting a .pdf
INPUT_FILE_PATH = "___.pdf"

# Define your output file name
# path MUST be a .csv file
OUTPUT_FILE_NAME = "___.csv"

# Define output directory ----
output_data_dir = os.path.join(, "", "")


# Set API Parameters -------------------------------------------
# Set the number of pages before and after page N to feed into Gemini when digitizing page N
page_window = 1
page_placement = "top"

# Define number of pages to digitize.
all_pages = True # If T, just does all the pages in the document
start_page = 145  # The starting page number in the file
n_pages = 6  # The number of pages (total) to digitize

# Indicate whether the pages should be saved as .png instead of .pdf
# ! NOTE: .png files must be a single page, so this only works with page_window=1
png = True

# SET GEMINI PROMPT ------------------------------------------------------------
# Indicate the file name for the prompt to use
prompt_text_name = "gemini_prompt_single_page.txt"


# ----------------------------------------------------------------------------------
# END OF SET PARAMETERS -------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# SET OUTPUT PATH  ------------------------------------------------------------

output_maindir = os.path.join(output_data_dir, "gemini_output")


# save each execution in a separate directory --- to ensure nothing is over-written
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#exe_dir = f"Run_{timestamp}__window{page_window}__place{page_placement}"
exe_dir = f"Run_{timestamp}__by{page_window}pages"
output_dir = os.path.join(output_maindir, exe_dir)

# Define the model you are going to use (flash is free with 1,500 requests per day)
gemini_model_id = "gemini-2.0-flash"  # or "gemini-2.0-flash-lite-preview-02-05"  , "gemini-2.0-pro-exp-02-05"

# ----------------------------------------------------------------------------------
# Set file paths -------------------------------------------------------------------
# ----------------------------------------------------------------------------------

prompt_text_path = os.path.join("prompts", prompt_text_name)


# Define logging function

def write_log(message, log_dir = output_dir):
    if not os.path.exists(os.path.join(log_dir,"logs")):
        os.makedirs(os.path.join(log_dir,"logs"))
    file_path = os.path.join(log_dir, "logs", "__log.txt")
    with open(file_path, "a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%H%M:%S")
        file.write(f"[{timestamp}] {message}\n\n")

def log_config(log_dir=output_dir):
    outdir = os.path.join(log_dir,"logs")
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Save text of gemini prompt--------
    with open(prompt_text_path, "r") as file:
        prompt_text = file.read()
    with open(os.path.join(outdir, "prompt_text.txt"), "a", encoding="utf-8") as file:
        file.write(prompt_text)

    # Save parameter values ----------
    file_path = os.path.join(log_dir,"logs", "__log.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file_path, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] \n\n")
        file.write(f"CONFIG PARAMETERS\n\n")
        file.write(f"Directory file year: {input_file_year}\n")
        file.write(f"Start page: {start_page}\n")
        file.write(f"End page: {start_page + n_pages -1}\n")
        file.write(f"Page window: {page_window}\n")
        file.write(f"Prompt text file: {prompt_text_name}\n")
        file.write(f"Gemini model: {gemini_model_id}\n\n")

# ----------------------------------------------------------------------------------
## ----------------------------------------------------------------------------------
