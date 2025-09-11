import requests
import polars as pl
from pathlib import Path
import re

# define filenames and URLs
medline_file = Path("medline_journal_list.txt")
doaj_file = Path("doaj_journal_list.csv")
output_path = Path("output/")

if not output_path.exists():
   output_path.mkdir()

medline_url = "https://ftp.ncbi.nih.gov/pubmed/J_Medline.txt"
doaj_url = "https://doaj.org/csv"

# download and save data
medline_journal_list = requests.get(medline_url).text
medline_file.write_text(medline_journal_list, encoding="UTF-8")

doaj_journal_list = requests.get(doaj_url).text
doaj_file.write_text(doaj_journal_list, encoding="UTF-8")

print("Downloaded datasets from DOAJ and MEDLINE")

# Parse PubMed text file
reg = re.compile(r"(?P<key>[a-zA-Z0-9\(\) ]+)\: (?P<val>.*)\n")
_medline_list = []
for j in medline_journal_list.split("--------------------------------------------------------\n"):
    m = reg.findall(j)
    if len(m) > 0:
        _medline_list.append(dict(m))

medline_journals = pl.DataFrame(_medline_list)
print("Converted MEDLINE dataset")

# Read DOAJ csv
doaj_journals = pl.read_csv(doaj_file)

def slugify(s):
  s = s.lower().strip()
  s = re.sub(r'[^\w\s-]', '', s)
  s = re.sub(r'[\s_-]+', '_', s)
  s = re.sub(r'^-+|-+$', '', s)
  return s

# get intersection of MEDLINE and DOAJ journal lists, based on ISSNs
doaj_medline_intersection = doaj_journals.filter(
    pl.col('Journal ISSN (print version)').is_in(medline_journals['ISSN (Print)'].to_list()) | pl.col('Journal EISSN (online version)').is_in(medline_journals['ISSN (Online)'].to_list())
).sort('Journal title').rename(lambda col: slugify(col))

# save files
doaj_medline_intersection.write_excel(output_path / "full_OA_journal_in_MEDLINE.xlsx")
doaj_medline_intersection.write_json(output_path / "full_OA_journal_in_MEDLINE.json")
print(f"Journal lists combined and written to {output_path} folder")