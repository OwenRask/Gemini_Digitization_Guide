import pandas as pd
from chardet.cli.chardetect import description_of
from pydantic import BaseModel, Field, StringConstraints
from typing import List, Dict, Optional, Union, Literal, Any, Annotated

class Entry(BaseModel):
    g: str = Field(description="entry group")
    n: str = Field(description="entry name")
    nu: str = Field(description="entry number")

class Page(BaseModel):
    n: int = Field(description="page number in the pdf")
    r: list[Entry] = Field(description="The list of entries on the page")

class Directory(BaseModel):
    p: list[Page] = Field(description="The list of pages in the pdf")


# Function to convert Directory to a DataFrame
def page_to_dataframe(page: Page):
    data = []

    for entry in page.r:
        #print(f"Processing Entry: {entry.o}")
                data.append({
                    "Group": entry.g,
                    "Name": entry.n,
                    "Number": entry.nu,
                    "Directory Page Number": page.n
                })

    df = pd.DataFrame(data)
    return df
