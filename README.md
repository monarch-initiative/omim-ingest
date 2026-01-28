# omim-ingest

Koza ingest for OMIM gene-to-disease associations, transforming morbidmap data into Biolink model format.

## Data Source

[OMIM](https://omim.org/) (Online Mendelian Inheritance in Man) is a comprehensive database of human genes and genetic phenotypes.

Data is downloaded from OMIM's data portal (requires access key).

## Output

This ingest produces:
- **Gene-to-disease associations** - Links OMIM gene entries to disease phenotypes
  - `CausalGeneToDiseaseAssociation` with `biolink:causes` for molecular basis known (3)
  - `CorrelatedGeneToDiseaseAssociation` with `biolink:contributes_to` for mapped associations (1, 2) and susceptibility markers

## Usage

```bash
# Set OMIM download key
export MONARCH_OMIM_DOWNLOAD_KEY=your_key_here

# Install dependencies
just install

# Run full pipeline
just run

# Or run steps individually
just download      # Download OMIM morbidmap
just transform-all # Run Koza transform
just test          # Run tests
```

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- [just](https://github.com/casey/just) command runner
- MONARCH_OMIM_DOWNLOAD_KEY environment variable

## License

BSD-3-Clause
