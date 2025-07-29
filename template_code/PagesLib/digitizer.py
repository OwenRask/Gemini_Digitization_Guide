from pydantic import BaseModel
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import time
import requests
import os
import pandas as pd
from pdf2image import convert_from_path
from PagesLib.Page_candidates import page_to_dataframe
# ----------------------------------------------------------------------------------
# -- Define functions --------------------------------------------------------------
# ----------------------------------------------------------------------------------

def check_pages(file_path, page_N, page_window, placement="middle"):
    """
    Determine the appropriate start and end page for a given page window.

    Parameters:
        file_path (str): Path to the PDF file.
        page_N (int): The target page number.
        page_window (int): Number of pages to include in the window.
        placement (str): Position of the target page within the window ('top', 'middle', 'bottom').

    Returns:
        tuple: (start_page, end_page) representing the range of selected pages.
    """

    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        total_page_count = len(reader.pages)

    # If the requested window is larger than the document, return the full document
    if page_window >= total_page_count:
        return 1, total_page_count  # Return the entire document

    # Ensure page_N is within valid range
    if page_N < 1 or page_N > total_page_count:
        raise ValueError(f"Page N ({page_N}) is out of document range (1-{total_page_count})")

    # Determine the start page based on placement
    if placement == "top":
        start_page = page_N
    elif placement == "middle":
        start_page = page_N - (page_window // 2)
    elif placement == "bottom":
        start_page = page_N - (page_window - 1)
    else:
        raise ValueError("Invalid placement. Choose from 'top', 'middle', or 'bottom'.")
    # Debugging

    # Ensure the start_page and n_pages fit within the document range
    if start_page < 1:
        start_page = 1
    if start_page + page_window - 1 > total_page_count:
        start_page = max(1, total_page_count - page_window + 1)  # Shift window left
    # Final page count
    n_pages = min(page_window, total_page_count - start_page + 1)

    # get end page
    end_page = start_page + n_pages -1

    return start_page, end_page


def check_document(file_path, all_pages=False, start_page=1, n_pages=1):
    """
    Validate the requested page range against the document length.

    Parameters:
        file_path (str): Path to the PDF file.
        all_pages (bool): If True, selects all pages.
        start_page (int): First page number to extract.
        n_pages (int): Number of pages to extract.

    Returns:
        tuple: (start_page, n_pages) after validation.
    """

    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        total_page_count = len(reader.pages)

    if all_pages:
        start_page = 1
        n_pages = total_page_count

    else:
        if total_page_count < (start_page + (n_pages - 1)):
            raise Exception(("Total pages requested exceeds document length!",
                                f"   Requested pages {start_page} to {start_page + (n_pages - 1)}",
                                f"but document only has {total_page_count} pages"))

    return start_page, n_pages

def upload_pages_to_API(genai_client, file_path: str, start_page: int, end_page:int, png=False):
    """
Uploads selected pages of a PDF (or PNG if requested) to the Gemini API.

Parameters:
    genai_client: Gemini API client.
    file_path (str): Path to the input PDF file.
    start_page (int): Starting page number.
    end_page (int): Ending page number.
    png (bool): If True, converts the page to PNG format.

Returns:
    object: Uploaded file object from the Gemini API.
"""
    file_name = f"{start_page}-{end_page}__{file_path.split('/')[-1].split('.')[0]}"

    if png and start_page == end_page:
        file_name = file_name + "_png"
    # Check if file already exists in the File API
    existing_files = genai_client.files.list()  # Get list of uploaded files
    uploaded_file = None
    for f in existing_files:
        if f.display_name == file_name:
            uploaded_file = f
            print(f"    File '{file_name}' already exists in the File API. Skipping upload.")
            break

    # Upload file  (only if it has not already been uploaded) ---------------

    # Create a temporary file ----
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_path = temp_file.name
    temp_file.close()  # Close the file so PyPDF2 can write to it

    if png and start_page==end_page:
        images = convert_from_path(file_path, first_page=start_page, last_page=end_page)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_path = temp_file.name
        temp_file.close()
        images[0].save(temp_path, 'PNG')
    else:
        reader = PdfReader(file_path)
        writer = PdfWriter()
        for i in range(start_page - 1, end_page):  # Convert 1-based to 0-based index
            writer.add_page(reader.pages[i])
        with open(temp_path, "wb") as output:
            writer.write(output)


    # Upload the file to the File API ---
    if not uploaded_file:
        print(f"    Uploading file: {file_name}")
        uploaded_file = genai_client.files.upload(
            file=temp_path, config={'display_name': file_name}
        )

    # delete tmp file after it's uploaded
    os.remove(temp_path)

    return uploaded_file

def extract_page_data(genai_client, input_file, model: BaseModel,
                      prompt_text: str, model_id="gemini-2.5-pro", debug=False):
    """
Extracts structured data from a page using the Gemini API.

Parameters:
    genai_client: Gemini API client.
    input_file: File object uploaded to the Gemini API.
    model (BaseModel): Data model for structuring extracted content.
    prompt_text (str): Prompt text for the API.
    model_id (str): Gemini model ID.
    debug (bool): Enables debug logging.

Returns:
    dict or None: Parsed structured data if successful, otherwise None.
"""
    # limit output size
    max_token_output = 40000
    max_retries = 5
    base_wait = 10       # this is in seconds!

    for attempt in range(max_retries):
        try:
            # Generate a structured response using the Gemini API ---
            response = genai_client.models.generate_content(
                model=model_id,
                contents=[prompt_text, input_file],
                config={'response_mime_type': 'application/json',
                        'response_schema': model,
                        'max_output_tokens': max_token_output})

            #print("API Response:", response)  # Debugging step
            #print(" Response Usage Metadata:", response.usage_metadata)

            # Added: Check for token limit issues
            if hasattr(response, 'candidates') and response.candidates:
                if response.candidates[0].finish_reason.name == 'MAX_TOKENS':
                    print(
                        f"WARNING: Response truncated due to token limit. Consider increasing max_output_tokens or splitting the page.")
                    print(f"Token count: {response.usage_metadata.candidates_token_count}")

            if debug:
                file_path = "output.txt"

                # Open the file in append mode and write text multiple times
                with open(file_path, "a", encoding="utf-8") as file:
                    for i in range(5):  # Writing 5 times
                        file.write(f"Line {i + 1}: This is some text being written.\n")

            if not response or not response.parsed:
                print("ERROR: The API did not return a valid parsed response.")
                return None

            return response.parsed

        # Add in a wat time response if the model is temporarily unavailable (error 503)
        except Exception as e:
            if '503' in str(e):
                wait_time = base_wait * (2 ** attempt)
                print(f"Error 503 on attempt {attempt + 1}. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
            else:
                print(f"EXCEPTION occurred (non-retryable): {e}")
                return None

    print("Max 503 error retries reached. Giving up on this page.")
    return None

def process_pages(genai_client, file_path: str, model: BaseModel, prompt_text: str, model_id: str,
                  total_pages: int, start_page: int, outfile_path: str,
                  page_window=1, page_placement="middle", png=False, debug=False):
    """
Extracts structured data from each page in the document and saves results.

Parameters:
    genai_client: Gemini API client.
    file_path (str): Path to the PDF file.
    model (BaseModel): Data model for structuring extracted content.
    prompt_text (str): Prompt text for the API.
    model_id (str): Gemini model ID.
    total_pages (int): Total number of pages to process.
    start_page (int): Starting page number.
    outfile_path (str): Path to save extracted data.
    page_window (int): Number of surrounding pages to include.
    page_placement (str): Placement of the target page within the window.
    png (bool): If True, converts pages to PNG before upload.
    debug (bool): Enables debug logging.

Returns:
    pd.DataFrame: Aggregated structured data extracted from the document.
"""

    all_dataframes = []
    max_retries = 5  # Set max retries to prevent infinite loops
    # check if all
    for N in range(start_page, (start_page + total_pages)): # recall, last number excluded in python range
        retries = 0
        success = False  # Track if the page was successfully processed

        # get subset of document pages to upload, based on page_window
        first_pg, last_pg = check_pages(file_path, N, page_window, page_placement)
        # Define prompt
        page_N_placement = N - first_pg + 1
        prompt = prompt_text.replace("PAGE_N", str(N))  # CAREFUL! Don't replace prompt template text
        prompt = prompt.replace("PAGE_PLACEMENT", str(page_N_placement))
        # print(prompt)  # DEBUGGING

        while retries < max_retries and not success:
            try:
                print(f"Processing page {N} (Attempt {retries + 1})...")

                # get uploaded pages
                uploaded_file = upload_pages_to_API(genai_client, file_path, first_pg, last_pg, png=png)

                # submit Gemini task prompt
                result = extract_page_data(genai_client, uploaded_file, model, prompt, model_id, debug)

                success = True
                if result:
                    df = page_to_dataframe(result)
                    # Add absolute page number
                    df["absolute_page_n"] = N

                    # Immediately delete the uploaded file so I don't reach the storage limit
                    try:
                        genai_client.files.delete(name=uploaded_file.name)
                        print(f"Deleted uploaded file: {uploaded_file.name}")
                    except Exception as e:
                        print(f"Warning: failed to delete uploaded file {uploaded_file.name}: {e}")

                else:
                    print(f"FAILURE - No data found for for page {N}.")

            except requests.exceptions.ConnectionError as e:
                print(f"Connection error on page {N}: {e}")
                retries += 1
                if retries < max_retries:
                    print(f"Retrying page {N} in 5 seconds...")
                    time.sleep(5)  # Wait before retrying
                else:
                    raise ValueError(f"Max retries reached for page {N}. Check your connection and try again")
                    break

        # Combine all output into one dataset
            all_dataframes.append(df)


            # write output to .csv file
            file_exists = os.path.exists(outfile_path)
            df.to_csv(outfile_path, mode="a", header=not file_exists, index=False)

    if all_dataframes:
        final_dataframe = pd.concat(all_dataframes, ignore_index=True)
        print(f"\n Generated dataframe with {df.shape[0]} rows")
        return final_dataframe
    else:
        return None



# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------