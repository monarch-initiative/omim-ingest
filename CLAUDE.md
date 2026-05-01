# omim-ingest

Koza ingest for OMIM gene-to-disease associations from the morbidmap.txt file.

## Project Structure

- `download.yaml` - Configuration for downloading OMIM morbidmap data (requires MONARCH_OMIM_DOWNLOAD_KEY)
- `src/` - Transform code and configuration
  - `transform.py` / `transform.yaml` - Main transform for gene-to-disease associations
  - `versions.py` - Per-ingest upstream version fetcher (consumed by `just metadata`)
- `scripts/write_metadata.py` - Emits `output/release-metadata.yaml` from `versions.py`
- `tests/` - Unit tests for transforms
- `output/` - Generated nodes and edges (gitignored)
  - `release-metadata.yaml` - Per-build manifest of upstream sources, versions, artifacts (kozahub-metadata-schema)
- `data/` - Downloaded source data (gitignored)

## Key Commands

- `just run` - Full pipeline (download -> transform)
- `just download` - Download OMIM morbidmap data
- `just transform-all` - Run all transforms
- `just transform <name>` - Run specific transform
- `just metadata` - Emit `output/release-metadata.yaml`
- `just test` - Run tests

## Data Notes

- Requires MONARCH_OMIM_DOWNLOAD_KEY environment variable for download
- Confidence levels (1-4) determine association type and predicate
- Susceptibility markers {} override confidence levels for contributes_to predicate
- Chromosomal abnormalities (4) are skipped

## Release Metadata

Every kozahub ingest emits an `output/release-metadata.yaml` describing the upstream sources, their versions, the artifacts produced, and the versions of build-time tools. This file is the contract monarch-ingest reads to assemble the merged knowledge graph's release receipt.

`src/versions.py` is the only per-ingest piece — it implements `get_source_versions()` returning a list of SourceVersion dicts. The `kozahub_metadata_schema` package provides reusable fetchers for the common patterns (HTTP Last-Modified, GitHub releases, URL-path regex, file-header parsing). The boilerplate (transform-content hashing, tool versions, build_version composition, yaml emission) is handled by `scripts/write_metadata.py`.

The `kozahub-metadata-schema` repo is expected as a sibling checkout (path-dep). Switch to a git or PyPI dep once published.

## Skills

- `.claude/skills/create-koza-ingest.md` - Create new koza ingests
- `.claude/skills/update-template.md` - Update to latest template version
