import csv
from pathlib import Path

nodes_report_file = Path("docs/nodes_report.tsv")
edges_report_file = Path("docs/edges_report.tsv")


def _load_edges_stats():
    """Load and parse edges report for stat lookups."""
    if not edges_report_file.exists():
        return {}

    stats = {}
    with open(edges_report_file, newline="\n") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        total = 0
        for row in reader:
            count = int(row['count_star()'])
            total += count
            predicate = row['predicate'].split(':')[-1]  # Extract "causes" from "biolink:causes"
            category = row['category'].split(':')[-1]    # Extract short name

            # Store by predicate
            stats[f"{predicate}_count"] = count

            # Store by category
            if category not in stats:
                stats[f"{category}_count"] = 0
            stats[f"{category}_count"] += count

        stats['total_edges'] = total

        # Calculate percentages
        if total > 0:
            for key in list(stats.keys()):
                if key.endswith('_count') and key != 'total_edges':
                    pct_key = key.replace('_count', '_pct')
                    stats[pct_key] = round(stats[key] / total * 100, 2)

    return stats


def define_env(env):
    """Define mkdocs macros."""

    # Load stats once
    _stats = _load_edges_stats()

    @env.macro
    def get_total_edges() -> str:
        """Get total edge count with comma formatting."""
        return f"{_stats.get('total_edges', 0):,}"

    @env.macro
    def get_stat(key: str) -> str:
        """Get a specific stat by key.

        Available keys:
        - total_edges
        - causes_count, causes_pct
        - contributes_to_count, contributes_to_pct
        - predisposes_to_condition_count, predisposes_to_condition_pct
        - CausalGeneToDiseaseAssociation_count, CausalGeneToDiseaseAssociation_pct
        - CorrelatedGeneToDiseaseAssociation_count, CorrelatedGeneToDiseaseAssociation_pct
        """
        value = _stats.get(key, 0)
        if isinstance(value, int):
            return f"{value:,}"
        return str(value)

    @env.macro
    def get_nodes_report() -> str:
        if not nodes_report_file.exists():
            return ""

        report = "## Nodes Report\n\n"
        with open(nodes_report_file, newline="\n") as csvfile:
            reader = csv.reader(csvfile, delimiter="\t")

            # turn into markdown table
            headers = next(reader)
            report += "|" + "|".join(headers) + "|\n"
            report += "|" + "|".join(["---" for _ in range(0, len(headers))]) + "|\n"
            for row in reader:
                report += "|" + "|".join(row) + "|\n"

        return report

    @env.macro
    def get_edges_report() -> str:
        if not edges_report_file.exists():
            return ""

        report = "## Edges Report\n\n"
        with open(edges_report_file, newline="\n") as csvfile:
            reader = csv.reader(csvfile, delimiter="\t")

            # turn into markdown table
            headers = next(reader)
            report += "|" + "|".join(headers) + "|\n"
            report += "|" + "|".join(["---" for _ in range(0, len(headers))]) + "|\n"
            for row in reader:
                report += "|" + "|".join(row) + "|\n"

        return report
