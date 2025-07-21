# Gemini_Digitization_Guide
This repository serves as a guide for John-Eric and Winnie’s pre-docs (as well as anyone else they share it with) on how to use Google’s Gemini API to digitize scanned documents. The process outlined here transforms complex historical documents into structured, usable data files. This README provides step-by-step instructions on how to run and customize the provided template code for any digitization task. The remainder of the document includes an outline with detailed guides and explanatory videos to support this process. When first learning the process, one should proceed by the numbered headers. I am HEAVILY indebted to Anna Crowley who drafted the inital versions of the code you will see in this guide and helped me learn this process. 

This guide was last edited on July 15th, 2025 by Owen Rask

# Overview of the Process

First, one must get the documents they desire to scan into a clear, pdf format. For the best scans possible, the pdfs should hopefully clear, visible, and and only contain the pages that have the desired to be digitized content. Second, based on the layout of the PDFs page, one will need to create a "Page Schema" that they will use to strucrture their pdf image into a captuable JSON format. Third, create a prompt that gives gemini a clear decription of what it should be looking for when reviewing the PDFs, including where the desired information is located on a page, what to extract from the page, what to ignore on the page, and some general 'controls'(no omitting entries/hallucinations). Fourth, set up the Config.py script to correctly input the pdfs and output the gemini digitization where desired. Fifth, run the whole process by executing the Main.py script. Sixth, check the output to the PDF and refine the prompt and Page Schema until it is a desired accuracy. 

# 1. Structuring the File to Digitize

You have spent some time compiling a bunch of government documents to digitize. One thing to know though, is that probably 30-40% of the accuracy of the digitization process relies on how clear and consistently scanned your documents are. While this obviously depends on how the document was obtained, below are a few tips that make the best structure of your documents.
  
  **1.A** If your document pages are not compiled into a PDF already, if scanning the individual pages as PNGs seems to be the best handeled by the digitizer code.  
  
  **1.B** Make all the pages you scan contain the information you want to digitize. THIS IS ESPECIALLY CRUCIAL FOR PAGE 1, OR ELSE IT WILL THROW AN ERROR. Thus, the first table or file should appear on page 1 of the combined PDF.  
  
  **1.C** Try as much as possible to crop/scan the images so that the individual pages have the same layout from page to page. Feeding gemini a few nicely scanned pages and then switching to pictures you took of the document on your phone with half of the image being the background of your surroudnings will reduce accuracy.  

A Video example where I prepare different types of images to digitize:  

# 2. Page Schema (Page.py)

# 3. Prompts 

# 4. Digitizer Code (Digitizer.py)

# 5. Bringing Everything Together (Config.py)

# 6. Running the Whole Process (Main.py)

# 7. Common Debugging Techniques and Issues

# 8. Checking the Output (generate_test_sample)

