import pandas as pd
import random
import sys
import os
from PyPDF2 import PdfReader, PdfWriter
import openpyxl

# ----------------------------------------------------------------------------------
# -- PARAMETERS---------------------------------------------------------------------
# ----------------------------------------------------------------------------------

PCT = 0.05  # Fraction of unique pages values to sample (e.g., 0.5 for 50%)
SEED = 42  # Random seed for reproducibility


# ----------------------------------------------------------------------------------
# -- SET PATHS ---------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# Get the parent directory and add it to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now you can import config
import config

# TO UPDATE FOR EACH DIGITIZED DIRECTORY SEPARATELY ---------------
year = "1974"
digitized_dir = os.path.join(config.data_dir, "raw_data", "urban_renewal_directories", "gemini_output",
                    year, "Run_2025-02-28_18-51-21__by1pages")

# General path definitions ---------------
os.makedirs(os.path.join(digitized_dir, "tests"), exist_ok=True)  # Create directory for test files if it doesn't exist


INPUT_CSV_FILE = os.path.join(digitized_dir, f"Urban_Renewal_Directory_{year}.csv")  # Path to the input CSV file

OUTPUT_CSV_FILE = os.path.join(digitized_dir, "tests", "directory_test_pages.csv")  # Path to save the output CSV file

OUTPUT_XLSX_FILE = os.path.join(digitized_dir, "tests", "directory_test_pages.xlsx")  # Path to save the output Excel file

INPUT_PDF_FILE = config.get_directory_filepath(year)  # Path to the input PDF file

OUTPUT_PDF_FILE = os.path.join(digitized_dir, "tests", "scanned_test_pages.pdf") # Path to save the filtered PDF


PCT = 0.05  # Fraction of unique pages values to sample (e.g., 0.5 for 50%)
SEED = 42  # Random seed for reproducibility

# ----------------------------------------------------------------------------------
# -- FUNCTIONS ---------------------------------------------------------------------
# ----------------------------------------------------------------------------------
def subset_by_pages(input_csv, output_csv, output_xlsx, pct, seed, input_pdf, output_pdf):
    # Set the random seed for reproducibility
    random.seed(seed)

    # Read the CSV file
    df = pd.read_csv(input_csv)

    # Ensure 'absolute_page_n' is an integer column
    df['absolute_page_n'] = pd.to_numeric(df['absolute_page_n'], errors='coerce').dropna().astype(int)

    # Check if 'PAGES' column exists
    if 'absolute_page_n' not in df.columns:
        raise ValueError("The input CSV must contain a 'absolute_page_n' column.")

    # Get unique pages values
    unique_pages = df['absolute_page_n'].unique()

    # Determine the number of pages to sample
    num_samples = max(1, int(len(unique_pages) * pct))

    # Randomly select a subset of pages
    sampled_pages = random.sample(list(unique_pages), num_samples)

    # Ensure sampled pages are integers
    sampled_pages = [int(page) for page in sampled_pages]

    # Filter the dataframe
    filtered_df = df[df['absolute_page_n'].isin(sampled_pages)]

    # Save to output CSV
    filtered_df.to_csv(output_csv, index=False)

    # Add test columns for user to fill in
    test_columns = [
        "Incorrect State", "Incorrect City Spelling", "Incorrect City Assignment",
        "Incorrect Project Name Spelling", "Incorrect Project Before",
        "Incorrect Project After", "Incorrect Project Type", "Incorrect Project ID",
        "Incorrect Planning Date", "Incorrect Execution Date", "Incorrect Completion Date",
        "Incorrect Project Approved Grants", "Incorrect Federal Grants Status",
        "Incorrect Project Disbursed Grants"
    ]

    # Add empty columns to the DataFrame
    for col in test_columns:
        df[col] = ""


    # Save to output Excel file
    filtered_df.to_excel(output_xlsx, index=False, engine='openpyxl')

    print(f"Filtered dataset saved to {output_csv} and {output_xlsx} with {len(filtered_df)} rows.")

    # Process PDF file
    extract_pdf_pages(input_pdf, output_pdf, sampled_pages)


def extract_pdf_pages(input_pdf, output_pdf, pages_to_keep):
    """Extracts selected pages from a PDF and saves a new PDF."""
    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        for page_num in sorted(pages_to_keep):  # Ensure order is maintained
            if 1 <= page_num <= len(reader.pages):  # Ensure page exists
                writer.add_page(reader.pages[page_num - 1])  # PDF pages are 0-indexed
            else:
                print(f"Warning: Page {page_num} is out of range and will be skipped.")

        # Save the new PDF
        with open(output_pdf, "wb") as output_file:
            writer.write(output_file)

        print(f"Filtered PDF saved to {output_pdf} with {len(writer.pages)} pages.")

    except Exception as e:
        print(f"Error processing PDF: {e}")



# ----------------------------------------------------------------------------------
# -- Execution ---------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# Run the function
subset_by_pages(INPUT_CSV_FILE, OUTPUT_CSV_FILE, OUTPUT_XLSX_FILE, PCT, SEED,
                INPUT_PDF_FILE, OUTPUT_PDF_FILE)


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------