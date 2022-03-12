import click

from . import DATADIR
from .extender import DatasetExtender


DEFAULT_OUTFILE = DATADIR / "dataset.snappy.parquet"


@click.command()
@click.option("-i", "--infile", help="Input dataset.", required=True)
@click.option("-o", "--outfile", help="Output file.", default=DEFAULT_OUTFILE)
@click.option("-s", "--skip", help="Number of rows to skip.", default=0)
def main(infile: str, outfile: str, skip: int):
    ex = DatasetExtender(infile, outfile, skip)
    ex.run()
    ex.write()


if __name__ == "__main__":
    main()
