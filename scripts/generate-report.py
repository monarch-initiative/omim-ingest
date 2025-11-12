from pathlib import Path
import shutil

import duckdb

nodes_file = "output/omim_gene_to_disease_nodes.tsv"
edges_file = "output/omim_gene_to_disease_edges.tsv"


# Nodes
if Path(nodes_file).exists():
    query = f"""
    SELECT category, split_part(id, ':', 1) as prefix, count(*)
    FROM '{nodes_file}'
    GROUP BY all
    ORDER BY all
    """
    output_path = "output/omim_gene_to_disease_nodes_report.tsv"
    duckdb.sql(f"copy ({query}) to '{output_path}' (header, delimiter '\t')")
    # Copy to docs for mkdocs
    shutil.copy(output_path, "docs/nodes_report.tsv")

# Edges
if Path(edges_file).exists():
    query = f"""
    SELECT category, split_part(subject, ':', 1) as subject_prefix, predicate,
    split_part(object, ':', 1) as object_prefix, count(*)
    FROM '{edges_file}'
    GROUP BY all
    ORDER BY all
    """
    output_path = "output/omim_gene_to_disease_edges_report.tsv"
    duckdb.sql(f"copy ({query}) to '{output_path}' (header, delimiter '\t')")
    # Copy to docs for mkdocs
    shutil.copy(output_path, "docs/edges_report.tsv")
