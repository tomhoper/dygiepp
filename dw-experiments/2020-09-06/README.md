Quick experiment to fix up the Chemprot data for Aida.

- `01_find_nan_docs.py`: Find documents that will produce `NaN`'s when run through encoder.
  - Inputs: `data/chemprot/mapped`, which is copied from `allgood:/data/aida/covid_aaai/UnifiedData/chemprot/mapped`.
  - Outputs: `data/chemprot/nan-docs`. One text file per doc, indicating the articles to throw out.
- `02_filter.py`: Filter the ChemProt data to remove `NaN`-causing documents, and any documents with no relations at all.
  - Inputs: `data/chemprot/mapped` and `data/chemprot/nan-docs`
  - Outputs: `data/chemprot/filtered`. I copied these back over to `allgood:/data/dave/proj/for-aida/chemprot-filtered-2020-09-05`.
