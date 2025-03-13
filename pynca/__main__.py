# PyNCA: Noncompartmental Analysis in Python
# Copyright (c) 2025 James S. Graydon
# Licensed under the MIT License (see LICENSE file)

import argparse
import pandas as pd
import sys
from .module import pk_dummy_data, pk_data

def parse_command_line():
    "parses args for the PyNCA functions"

    # init parser and add arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--generate",
        help="generates a dummy dataset of PK data",
        action="store_true"
        )

    parser.add_argument(
        "--dummy_n_ids",
        help="sets number of ID values for the dummy dataset",
        dest='d_nids', 
        type=int,
        required="--generate" in parser.parse_known_args()[0]
        )

    parser.add_argument(
        "--dummy_times",
        help="Sets sampling times for dummy dataset",
        dest="d_times",
        nargs="+",   
        type=float,  
        required="--generate" in parser.parse_known_args()[0]
        )

    parser.add_argument(
        "--dummy_dose",
        help="sets dose for dummy dataset",
        dest='d_dose', 
        type=float,
        required="--generate" in parser.parse_known_args()[0]
        )

    parser.add_argument(
        "--dummy_half_life",
        help="sets half-life for dummy dataset",
        dest='d_t12', 
        type=float,
        required="--generate" in parser.parse_known_args()[0]
        )

    parser.add_argument(
        "-f",
        "--file",
        help="provide file path to a CSV file",
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
        help="option to summarize the data (mean, SD) before plotting (requires -/--plot)",
        action="store_true"
        )

    parser.add_argument(
        "--log_scale",
        help="option to plot the data on a semi-log scale (requires -p/--plot)",
        action="store_true"
        )

    parser.add_argument(
        "--auc_start",
        help="first time value to include in AUC (requires -r/--report)",
        type=int,
        dest="auc_start"
        )

    parser.add_argument(
        "--auc_end",
        help="last time value to include in AUC (requires -r/--report)",
        type=int,
        dest="auc_end"
        )

    parser.add_argument(
        "--terminal_times",
        help="list of times for half-life calculation (requires -r/--report)",
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
        help="Name for saved NCA results",
        dest="report_path"
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
            print(f"📊 Summary statistics for {args.file}:\n")
            print(df.summarize())

        if args.plot:
            print(  "\nGenerating plot...\n")
            fig = df.plot(summarized = args.plot_mean, log_scale = args.log_scale)
            plot_file = "pk_plot.html"
            fig.write_html(plot_file)
            print(f"\n📂 Plot saved as {plot_file}. Open it in a web browser to view.\n")

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