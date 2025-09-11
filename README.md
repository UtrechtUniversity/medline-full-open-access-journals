# Full OA journals in MEDLINE

This set of scripts generates a list of journals that are classified as full open access by the [DOAJ](https://doaj.org) and indexed in [MEDLINE](https://www.nlm.nih.gov/medline/medline_home.html).

## Working principle

It consists of two parts, the data downloader (`main.py`) and an interactive data viewer (`index.html`). `main.py` downloads data from the DOAJ and MEDLINE (NLM), intersects both lists based on the ISSNs and subsequently outputs the data as an Excel file and a json file. The interactive viewer then loads the json file and displays it using [AG Grid](https://www.ag-grid.com/).

## Online interactive viewer

The interactive table can be accessed through [https://utrechtuniversity.github.io/medline-full-open-access-journals/](https://utrechtuniversity.github.io/medline-full-open-access-journals/). 