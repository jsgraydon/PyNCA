# PyNCA: Noncompartmental Analysis in Python
# Copyright (c) 2025 James S. Graydon
# Licensed under the MIT License (see LICENSE file)

import argparse
import pandas as pd
import os
import sys
import subprocess
from .module import pk_dummy_data, pk_data

def parse_command_line():
    "parses args for the PyNCA functions"

    # init parser and add arguments
    parser = argparse.ArgumentParser(description="PyNCA: Noncompartmental Analysis in Python",
    epilog="""\
Example usage:

  # Generate a dummy dataset 
  python -m pynca --generate --dummy_n_ids 10 --dummy_times 0 1 2 4 8 --dummy_dose 100 --dummy_half_life 3.5

  # Load a dataset and summarize
  python -m pynca -f [data.csv] --summarize

  # Plot the raw data with a semi-log scale
  python -m pynca -f [data.csv] -p --log_scale

  # Perform a full NCA analysis
  python -m pynca -f [data.csv] --nca --auc_start 0 --auc_end 8 --terminal_times 1 2 4

For more details, please see the README file.
""", formatter_class=argparse.RawTextHelpFormatter
)

    parser.add_argument(
        "--generate",
        help="generates a dummy dataset of PK data",
        action="store_true"
        )

    parser.add_argument(
        "--dummy_n_ids",
        help="int: sets number of ID values for the dummy dataset (requires --generate)",
        dest='d_nids', 
        type=int
        )

    parser.add_argument(
        "--dummy_times",
        help="list (space-seperated): sets sampling times for dummy dataset (requires --generate)",
        dest="d_times",
        nargs="+",   
        type=float
        )

    parser.add_argument(
        "--dummy_dose",
        help="float: sets dose for dummy dataset (requires --generate)",
        dest='d_dose', 
        type=float
        )

    parser.add_argument(
        "--dummy_half_life",
        help="float: sets half-life for dummy dataset (requires --generate)",
        dest='d_t12', 
        type=float
        )

    parser.add_argument(
        "-f",
        "--file",
        help="str: provide file path to a CSV file",
        dest="dataset_path",
        type=str
        )

    parser.add_argument(
        "-s",
        "--summarize",
        help="summarize the data (requires -f/--file)",
        action="store_true"
        )

    parser.add_argument(
        "-p",
        "--plot",
        help="plot the raw data (requires -f/--file)",
        action="store_true"
        )

    parser.add_argument(
        "--plot_mean",
        help="option to summarize the data (mean, SD) before plotting (requires -p/--plot)",
        action="store_true"
        )

    parser.add_argument(
        "--log_scale",
        help="option to plot the data on a semi-log scale (requires -p/--plot)",
        action="store_true"
        )
    
    parser.add_argument(
        "-t",
        "--half_life",
        help="option to calculate half-life (requires -f/--file and --terminal_times)",
        action="store_true"
        )

    parser.add_argument(
        "--auc_start",
        help="int: first time value to include in AUC (requires -r/--report)",
        type=int,
        dest="auc_start"
        )

    parser.add_argument(
        "--auc_end",
        help="int: last time value to include in AUC (requires -r/--report)",
        type=int,
        dest="auc_end"
        )

    parser.add_argument(
        "--terminal_times",
        help="list (space-separated): list of times for half-life calculation (requires -r/--report)",
        nargs="+",
        type=float,
        dest="term_times"
        )

    parser.add_argument(
        "--auc",
        help="calculates AUC between --auc_start and --auc_end",
        action="store_true"
        )

    parser.add_argument(
        "--nca",
        help="perform full NCA (requires -f/--file)",
        action="store_true"
        )

    parser.add_argument(
        "--report",
        help="str: name for saved NCA results",
        type=str,
        dest="report_path"
        )
    
    parser.add_argument(
        "--streamlit",
        help="launch PyNCA in a Streamlit app",
        action="store_true"
        )

    # parse args
    args = parser.parse_args()

    if args.generate:
        if args.d_nids is None:
            args.d_nids = int(input("Enter the number of ID values for the dummy dataset: "))
        if args.d_times is None:
            args.d_times = list(map(float, input("Enter sampling times (space-separated): ").split()))
        if args.d_dose is None:
            args.d_dose = list(map(float, input("Enter dose value: ").split()))
        if args.d_t12 is None:
            args.d_t12 = float(input("Enter the half-life value: "))
    
    return args


def main():
    "run main function on parsed args"

    # get arguments from command line as a dict-like object
    args = parse_command_line()

    if args.streamlit:
        subprocess.run(["streamlit", "run", os.path.join(os.path.dirname(os.path.abspath(__file__)), "pynca-sl.py")])

    if (args.log_scale or args.plot_mean) and not args.plot:
        print("\n❌ Error: Plotting options supplied without -p/--plot. Please add the -p flag.\n")
        return

    if args.generate:
        print("\nGenerating dummy PK dataset...\n")

        dummy = pk_dummy_data(n_ids=args.d_nids, times=args.d_times, dose=args.d_dose)
        dummy.iv_bolus_1cmt(half_life=args.d_t12)
        dummy.df.to_csv("pk_dummy_iv_bolus_1cmt.csv", index=False)
        print("\n✅ Dummy dataset saved as 'generated_dummy_data.csv'\n")

    if args.dataset_path is not None:
        df = pk_data(data = args.dataset_path)
        if args.summarize:
            print(f"📊 Summary statistics for {args.dataset_path}:\n")
            print(df.summarize())

        if args.plot:
            print(  "\nGenerating plot...\n")
            fig = df.plot(summarized = args.plot_mean, log_scale = args.log_scale)
            plot_file = "pk_plot.html"
            fig.write_html(plot_file)
            print(f"\n📂 Plot saved as {plot_file}. Open it in a web browser to view.\n")

        if args.half_life:
            if args.term_times is None:
                print("\n ❌Error: Half-life cannot be calculated with terminal elimination timepoints (--termal_times)")
                return
            print(f"Calculating half-life using terminal elimination phase: {args.term_times}...")
            half_life = df.half_life(term_elim_times=args.term_times)
            print(half_life)

        if args.auc:
            print(f"\nCalculating AUC between {args.auc_start} and {args.auc_end}...")
            auc = df.auc(start = args.auc_start, end = args.auc_end)
            print(auc)

        if args.nca:
            print("\nAnalyzing data...\n")
            df.report(term_elim_times=args.term_times, start=args.auc_start, end=args.auc_end)
            if args.report_path is not None:
                if not args.report_path.endswith(".txt"):
                    args.report_path += ".txt"
                with open(args.report_path, "w") as f:
                    sys.stdout = f  # Redirect print output
                    df.report(term_elim_times=args.term_times, start=args.auc_start, end=args.auc_end)
                sys.stdout = sys.__stdout__
                print(f"📝 Report saved as text file at {args.report_path}.")


# Ensure main() runs when script is executed
if __name__ == "__main__":
    main()