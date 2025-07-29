import pandas as pd
from chardet.cli.chardetect import description_of
from pydantic import BaseModel, Field, StringConstraints
from typing import List, Dict, Optional, Union, Literal, Any, Annotated

class Entry(BaseModel):
    g: str = Field(description="entry group")
    e: int = Field(description="entry inscrição (enrollment) number")
    n: str = Field(description="entry nome (name)")
    c: str = Field(description="entry CPF number")
    nc: str = Field(description="entry spouse nome (name)")
    cc: str = Field(description="entry spouse CPF number")

class Page(BaseModel):
    n: int = Field(description="page number in the lottery pdf")
    r: list[Entry] = Field(description="The list of entries on the page (rows)")

class Directory(BaseModel):
    p: list[Page] = Field(description="The list of pages in the lottery")


# Function to convert Directory to a DataFrame
def page_to_dataframe(page: Page):
    data = []

    for entry in page.r:
        #print(f"Processing Entry: {entry.o}")
                data.append({
                    "Grupo": entry.g,
                    "inscrição": entry.e,
                    "Nome": entry.n,
                    "CPF": entry.c,
                    "Conjuge_Nome": entry.nc,
                    "Conjuge_CPF": entry.cc,
                    "Directory Page Number": page.n
                })

    df = pd.DataFrame(data)
    return df