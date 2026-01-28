# omim-ingest

Koza ingest for OMIM gene-to-disease associations from the morbidmap.txt file.

## Project Structure

- `download.yaml` - Configuration for downloading OMIM morbidmap data (requires MONARCH_OMIM_DOWNLOAD_KEY)
- `src/` - Transform code and configuration
  - `transform.py` / `transform.yaml` - Main transform for gene-to-disease associations
- `tests/` - Unit tests for transforms
- `output/` - Generated nodes and edges (gitignored)
- `data/` - Downloaded source data (gitignored)

## Key Commands

- `just run` - Full pipeline (download -> transform)
- `just download` - Download OMIM morbidmap data
- `just transform-all` - Run all transforms
- `just test` - Run tests

## Data Notes

- Requires MONARCH_OMIM_DOWNLOAD_KEY environment variable for download
- Confidence levels (1-4) determine association type and predicate
- Susceptibility markers {} override confidence levels for contributes_to predicate
- Chromosomal abnormalities (4) are skipped
