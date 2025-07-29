# Generate test sample

The __main__.py script reads in a digitized directory (a `.csv` file) and randomly selects a fraction of the directory pages for verifying data quality with the scanned directory. 

It outputs:

 -   a  `.csv` of the digitized sampled pages
 -   a `.pdf` of the corresponding scanned pages of the directory
 - an `.xlsx` file of the sampled pages with columns for the human verifier to fill in as they are comparing the excel file to the scanned pages.

The outputs are written to a "tests" subfolder where the digitized directory is located.

## Verifying the data 
To evaluate the test sample, open the `.xlsx` file and compare each project to the scanned directory in the `.pdf` file.
The  `.xlsx` file has empty columns f.or evaluating each data cell. Enter a "1" if the data is incorrect. Leave it blank if the data is incorrect
