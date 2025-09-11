import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import requests
    import polars as pl
    from pathlib import Path
    return Path, mo, pl, requests


@app.cell
def _(mo):
    mo.md(
        r"""
    # About this document

    This interactive notebook downloads the latest [MEDLINE journal list](https://ftp.ncbi.nih.gov/pubmed/J_Medline.txt) (data provided by [NLM](https://www.nlm.nih.gov/)) and list of journals indexed in the [Directory of Open Access Journals (DOAJ)](https://doaj.org) (data CC BY-SA DOAJ).

    The script then checks for all DOAJ journals, whether they are indexed in MEDLINE and returns only the journals for which this is true. The result is a list of full Open Access journals, indexed in MEDLINE.
    """
    )
    return


@app.cell
def _(mo):
    overwrite = mo.ui.checkbox(label="Overwrite local files?")
    overwrite
    return (overwrite,)


@app.cell
def _(Path):
    pubmed_file = Path("pubmed_journal_list.txt")
    doaj_file = Path("doaj_journal_list.csv")
    return doaj_file, pubmed_file


@app.cell
def _(mo):
    mo.md(r"""## 1. Downloading data""")
    return


@app.cell
def _(doaj_file, mo, overwrite, pubmed_file, requests):
    pubmed_url = "https://ftp.ncbi.nih.gov/pubmed/J_Medline.txt"
    doaj_url = "https://doaj.org/csv"
    messages = []

    if pubmed_file.exists() and not overwrite.value:
        # load data from file
        pubmed_journal_list = pubmed_file.read_text(encoding="UTF-8")
        messages.append("PubMed journals read from file")
    else:
        # renew data and save to file
        pubmed_journal_list = requests.get(pubmed_url).text
        pubmed_file.write_text(pubmed_journal_list, encoding="UTF-8")
        messages.append("PubMed journals downloaded and saved to file")

    if doaj_file.exists() and not overwrite.value:
        # load data from file
        doaj_journal_list = doaj_file.read_text(encoding="UTF-8")
        messages.append("DOAJ journals read from file")
    else:
        # renew data and save to file
        doaj_journal_list = requests.get(doaj_url).text
        doaj_file.write_text(doaj_journal_list, encoding="UTF-8")
        messages.append("DOAJ journals downloaded and saved to file")

    mo.vstack(messages)
    return (pubmed_journal_list,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 2. Parse data

    Convert the text/csv files to a [polars](https://pola.rs) dataframe
    """
    )
    return


@app.cell
def _(mo, pl, pubmed_journal_list):
    # Parse PubMed text file
    import re
    reg = re.compile(r"(?P<key>[a-zA-Z0-9\(\) ]+)\: (?P<val>.*)\n")
    _pubmed_list = []
    for j in pubmed_journal_list.split("--------------------------------------------------------\n"):
        m = reg.findall(j)
        if len(m) > 0:
            _pubmed_list.append(dict(m))

    pubmed_journals = pl.DataFrame(_pubmed_list)
    mo.vstack([mo.md("### PubMed journals"), pubmed_journals])
    return pubmed_journals, re


@app.cell
def _(doaj_file, mo, pl):
    # Read DOAJ csv
    doaj_journals = pl.read_csv(doaj_file)
    mo.vstack([mo.md("### DOAJ journals"), doaj_journals])
    return (doaj_journals,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 3. Output journals

    Selecting only the journals from the DOAJ that are also indexed in MEDLINE.
    """
    )
    return


@app.cell
def _(doaj_journals, mo, pl):
    doaj_subset = doaj_journals.filter(
        pl.col('APC') == 'No',
        pl.col('Has other fees') == 'No',
    )
    mo.vstack([mo.md("### DOAJ journals without APCs/other charges"), doaj_subset])
    return


@app.cell
def _(re):
    from re import sub
    def slugify(s):
      s = s.lower().strip()
      s = re.sub(r'[^\w\s-]', '', s)
      s = re.sub(r'[\s_-]+', '_', s)
      s = re.sub(r'^-+|-+$', '', s)
      return s
    return (slugify,)


@app.cell
def _(doaj_journals, mo, pl, pubmed_journals, slugify):
    doaj_pubmed_intersection = doaj_journals.filter(
        pl.col('Journal ISSN (print version)').is_in(pubmed_journals['ISSN (Print)'].to_list()) | pl.col('Journal EISSN (online version)').is_in(pubmed_journals['ISSN (Online)'].to_list())
    ).sort('Journal title').rename(lambda col: slugify(col))
    doaj_pubmed_intersection.write_excel("full_OA_journal_in_MEDLINE.xlsx")
    doaj_pubmed_intersection.write_json("full_OA_journal_in_MEDLINE.json")
    mo.vstack([mo.md("## Full OA journals, indexed in MEDLINE"), doaj_pubmed_intersection])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
