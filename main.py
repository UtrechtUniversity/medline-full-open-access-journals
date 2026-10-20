import requests
import polars as pl
from pathlib import Path
import re
import os

if "OPENALEX_API_KEY" not in os.environ:
    import sys

    print(
        "Error: OPENALEX_API_KEY environment variable missing, please set to valid API key"
    )
    sys.exit(1)

# define filenames and URLs
doaj_file = Path("doaj_journal_list.csv")
output_path = Path("output/")

if not output_path.exists():
    output_path.mkdir()

doaj_url = "https://doaj.org/csv"

# download and save data
doaj_journal_list = requests.get(doaj_url).text
doaj_file.write_text(doaj_journal_list, encoding="UTF-8")

print("Downloaded dataset from DOAJ")

# Download ISSNs from OpenAlex medline index
cursor = "*"
ISSNs = []
while cursor:
    r = requests.get(
        f"https://api.openalex.org/sources",
        params={
            "filter": "listed_in:medline",
            "select": "issn",
            "per_page": 100,
            "cursor": cursor,
            "api_key": os.environ.get("OPENALEX_API_KEY"),
        },
    ).json()

    for res in r["results"]:
        ISSNs.extend(res["issn"])

    cursor = r["meta"].get("next_cursor")

print("Downloaded MEDLINE journal list from OpenAlex")

# Read DOAJ csv
doaj_journals = pl.read_csv(doaj_file)


def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "_", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s


# get intersection of MEDLINE and DOAJ journal lists, based on ISSNs
doaj_medline_intersection = (
    doaj_journals.filter(
        pl.col("Journal ISSN (print version)").is_in(ISSNs)
        | pl.col("Journal EISSN (online version)").is_in(ISSNs)
    )
    .sort("Journal title")
    .rename(lambda col: slugify(col))
)

# save files
doaj_medline_intersection.write_excel(output_path / "full_OA_journal_in_MEDLINE.xlsx")
doaj_medline_intersection.select(
    pl.col("journal_title"),
    pl.col("apc"),
    pl.col("has_other_fees"),
    pl.col("publisher"),
    pl.col("subjects"),
    pl.col("apc_amount"),
    pl.col("languages_in_which_the_journal_accepts_manuscripts"),
    pl.col("url_in_doaj"),
    pl.col("journal_url"),
    pl.col("journal_license"),
    pl.col("journal_issn_print_version"),
    pl.col("journal_eissn_online_version"),
).write_json(output_path / "full_OA_journal_in_MEDLINE.json")
print(f"Journal lists combined and written to {output_path} folder")
