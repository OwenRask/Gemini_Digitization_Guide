# Gemini_Digitization_Guide
This repository serves as a guide for John-Eric and Winnie’s pre-docs (as well as anyone else they share it with) on how to use Google’s Gemini API to digitize scanned documents. The process outlined here transforms complex historical documents into structured, usable data files. This README provides step-by-step instructions on how to run and customize the provided template code for any digitization task. The remainder of the document includes an outline with detailed guides and explanatory videos to support this process. When first learning the process, one should proceed by the numbered headers. I am HEAVILY indebted to Anna Crowley who drafted the inital versions of the code you will see in this guide and helped me learn this process. 

This guide was last edited on July 15th, 2025 by Owen Rask

# Overview of the Whole Process

First, one must get the documents they desire to scan into a clear, pdf format. For the best scans possible, the pdfs should hopefully clear, visible, and and only contain the pages that have the desired to be digitized content. Second, based on the layout of the PDFs page, one will need to create a "Page Schema" that they will use to strucrture their pdf image into a captuable JSON format. Third, create a prompt that gives gemini a clear decription of what it should be looking for when reviewing the PDFs, including where the desired information is located on a page, what to extract from the page, what to ignore on the page, and some general 'controls'(no omitting entries/hallucinations). Fourth, set up the Config.py script to correctly input the pdfs and output the gemini digitization where desired. Fifth, run the whole process by executing the Main.py script. Sixth, check the output to the PDF and refine the prompt and Page Schema until it is a desired accuracy. 

# 1. Structuring the File to Digitize

You have spent some time compiling a bunch of government documents to digitize. One thing to know though, is that probably 30-40% of the accuracy of the digitization process relies on how clear and consistently scanned your documents are. While this obviously depends on how the document was obtained, below are a few tips that make the best structure of your documents.

**1.A** If your document pages are not compiled into a PDF already, scanning the individual pages as PNGs seems to be the best image format that is handeled by the digitizer code.  
  
**1.B** Make all the pages you scan contain the information you want to digitize. THIS IS ESPECIALLY CRUCIAL FOR PAGE 1, OR ELSE IT WILL THROW AN ERROR. Thus, the first table or file should appear on page 1 of the combined PDF.  
  
**1.C** Try as much as possible to crop/scan the images so that the individual pages have the same layout from page to page. Feeding gemini a few nicely scanned pages and then switching to pictures you took of the document on your phone with half of the image being the background of your surroudnings will reduce accuracy.  

A Video example where I prepare different types of images to digitize:  

# 2. Page Schema (Page.py)

Ok, now you have your document fully scanned and ready to digitize. The next step is deciding what information you want to extract from that document, and how it is going to be structured in your output. This is the job of the Page Schema. The Page Schema accomplishes two things. First, it tells gemini what JSON type/format it should be looking for and extracting on each page, and second, it defines how your extracted data will be compiled into a final csv output. Thus, the page schema accounts for roughly 20% of the accuracy of your digitization process. Below are a few pointers to keep in mind when constructing your Page Schema.

**2.A** Currently, the template digitization process is built around processing one type of page at a time. For that reason, if for half of a document you want to capture say, 4 columns, but then for the other half you only want to capture 2 columns, you can either write a page schema to capture all of them and delete the one's you don't want later or you need to create two different page schema's and process the two halfs of the document separately. This often comes into play when one is digitizing a series of government documents over many years, and the format or information in those documents is added or removed across the time.

**2.B** To be able to process many pages at a time, think of every Page Schema as a heirarchical structure. Referencing the template provided, One starts with a 'Directory' of pages (the whole PDF), and each 'Directory' has a list of pages. Then, for each page, there are a list of 'Entries' (the rows of data on that page). Lastly, for each 'Entry', there is a bunch of individual information one wants to extract which would be the pages columns, for example.

**2.C** When defining what data one wants to extract for each entry, using the different types of data restrictions from Python's "typing" package is super helpful. If there are only two options for a column (say yes or no), make that Entry attribute 'Literal["yes", "no"]', and gemini will only be able to return a yes or a no in that slot. If I want to extract a number, I would usually use the type 'int', however 'int' does not capture numbers with decimals well, so I could define it as 'Union[str, int]' (or if the response can be written as 5 or five). Understanding how best to define your data so gemini captures and extracts what one wants is a trial and error process, but once one gets the hang of making Page Schemas, it comes quite easily. 

**2.D** While one can spend a long time constructing their Page Schema, do not ignore the page_to_datafram function, as it is the actual method which will turn the extracted JSON data into what appears in your final CSV. 

A Video example where I discuss different Page Schemas and spend more time discussing the actual code:  

# 3. Prompts 

You have your cleaned PDFs and your Page Schema to extract the infromation from those images, next you need to instruct gemini to do that task! This is where prompts come in, and they account for almost half (50%) of how accurate your digitized output will be. The foundational points with prompts are this: they require consistent experimentation and refining. Each prompt should be incredibly tailored to the document you are digitizing. It is essential to remember that more information in a prompt does not always equal a better output. Try to be concise and clear in your prompt, the less gemini has conflicting instrucctions the better. For these reasons, prompts can take many forms, and thus I highly recommend watching the below video where I go through different types of documents and the prompts I found were the most successful after many iterations. Regardless of the document though, below are a few pointers for things that should always be included in your prompts.

**3.A** You should always mention that you want gemini to return the information as JSON and that it should follow the Page Schema provided.

**3.B** Sectioned and hierarchical directions appear to be quite effective. I usually split my prompts into 5 main sections: (i) General Instructions, (ii) Page Handeling Rules, (iii) Extraction Rules, (iv) Output Rules, and (v) Important Constraints. 

**3.C** Always try to include some language asking gemini to (i) not omit any entries, (ii) do not make up or hallucinate or make up any entries, and (iii) waht information it should ignore on the page (ex: anything but what you want to extract). Adding some protection against gemini making up information when it does not know what something is important. Another good way to guard against this is instrucctions like 'when field x is blank, return NA'.

**3.D** When explaining what gemini should be looking for and extracting from each page, the important 'directions' you should always provide are (i) location: is it indented from a previous data point? Is it always in a box or neat specific wording? Is it always on a specific part of the page or column? Etc. And (ii) format: it is a date so it will be in the 'YY-MM', is it a numeric or monetary value? Does it only take on specific values ("yes" or "no")? Is it always underlined or bolded? Etc. 

# 4. Digitizer Code (Digitizer.py)

You have all the pieces (cleaned PDF, Page Schema, and prompt) assembled, so it is time to actual run the digitization code! The 'Digitizer.py' script houses all the functions that actually run the digitization process. In practice, this file should be rarely changed, usually only edited to (i) add more safe-guards into the process, (ii) to debug what is going wrong digitization is not working, and (iii) updated when new models of gemini or the python SDK are released. Below are a discussion of some parameters and helpful debugging code I have currently built into the digitizer.py script, which will need to be uncommented to use. See the below video for a full review of the digitizer.py script.

**4.A** In the extract_page_data function, three parameters are defined: (i) max_token_output which is set at 40,000 and adjusting this depends on how much information you are extracting from each page, (ii) max_retries, and (iii) base_wait which are used when the code runs into a gemini error (any error in the 500 range is a google side error).

**4.B** In the extract_page_data function, there are two lines that provide most of the debugging help when uncommented. First is the line: 'print("API Response: ", response).' When this is uncommented, the script will then display the raw extracted gemini JSON material from that page (in the Page Schema format). Use this to see how well gemini is understanding and extracting the image information from your prompt + Page Schema provided. Second is the line: 'print(" Response Usage Metadata:", response.usage_metadata).' Uncomment this line to see how many input and output tokens your prompt + page extraction process requires. I discuss more about token tracking and payment scheme below in Section #9.  

# 5. Bringing Everything Together (Config.py)

# 6. Running the Whole Process (Main.py)

# 7. Common Debugging Techniques and Issues

# 8. Checking the Output (generate_test_sample)

# 9. Understanding the Google Gemini Universe (Usage, Limits, Models, etc.)

