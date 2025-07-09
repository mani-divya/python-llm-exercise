"""
CLI entry point for paperslist.
"""
import sys
import click
import pandas as pd
from typing import Optional
from .pubmed import fetch_pubmed_ids, fetch_pubmed_details

@click.command()
@click.argument("query")
@click.option("-f", "--file", "filename", type=click.Path(), help="Filename to save results as CSV. Prints to console if not provided.")
@click.option("-d", "--debug", is_flag=True, help="Print debug information during execution.")
def main(query: str, filename: Optional[str], debug: bool):
    """Fetch PubMed papers for QUERY and output filtered results."""
    if debug:
        click.echo(f"Fetching PubMed IDs for query: {query}")
    ids = fetch_pubmed_ids(query)
    if debug:
        click.echo(f"Found {len(ids)} PubMed IDs. Fetching details...")
    papers = fetch_pubmed_details(ids)
    if debug:
        click.echo(f"Filtered to {len(papers)} papers with non-academic authors.")
    df = pd.DataFrame([p.to_dict() for p in papers if p.non_academic_authors])
    if filename:
        df.to_csv(filename, index=False)
        click.echo(f"Results saved to {filename}")
    else:
        click.echo(df.to_csv(index=False))

if __name__ == "__main__":
    main()
