"""AWR Tools CLI -- export graph traces and parse MWO data files."""

import argparse
import sys


def cmd_export(args):
    """Export all graph traces from an AWR project."""
    import awr_export

    awr_export.export_all_graph_traces(
        export_dir=args.output_dir,
    )


def cmd_parse(args):
    """Parse an MWO data file and print a summary."""
    import MWO_Parser

    parser = MWO_Parser.APFileParser(args.file)
    df = parser.get_dataframe()

    print(f"Columns: {len(df.columns)}  Rows: {len(df)}")
    print(f"Column names: {list(df.columns)}")
    print()
    print(df.head().to_string())


def main():
    parser = argparse.ArgumentParser(
        description="AWR Tools -- export graph traces and parse MWO data files",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- export subcommand ---
    sp_export = subparsers.add_parser(
        "export",
        help="Export all graph traces from the open AWR project",
    )
    sp_export.add_argument(
        "--output-dir",
        metavar="PATH",
        default=None,
        help="Directory for exported files (opens folder dialog if omitted)",
    )
    sp_export.set_defaults(func=cmd_export)

    # --- parse subcommand ---
    sp_parse = subparsers.add_parser(
        "parse",
        help="Parse an MWO data file and print a summary",
    )
    sp_parse.add_argument(
        "file",
        metavar="FILE",
        help="Path to the MWO data file to parse",
    )
    sp_parse.set_defaults(func=cmd_parse)

    # --- dispatch ---
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
