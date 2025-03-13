# PyNCA: Noncompartmental Analysis in Python
*Copyright (c) 2025 James S. Graydon*
*Licensed under the MIT License (see LICENSE file)*

PyNCA is a **free**, **open-source**, and **Python-based** package intended to provide tools for performing **noncompartmental analysis (NCA)** on pharmacokinetic (PK) data in a local environment with minimal dependencies. 

*NB: PyNCA is intended to be used via a graphic-user interface (GUI); however, at this time, only the command-line interface (CLI) functionality has been implemented.*

### Requirements

PyNCA is designed to rely on a minimal number of dependencies, namely:
- *pandas*
- *numpy*
- *plotly*
- *scipy.stats* 
- *PySide6*

### Installation

The following instructions will install the required packages, create a clone of the PyNCA repository, and install the project.

1. Enter the following code to install the required packages:
```
conda install pandas numpy plotly scipy.stats pyside6 -c conda-forge
```

2. Clone the repository:
```
git clone https://github.com/jsgraydon/pynca.git
```

3. Enter the project directory and install the project in editable mode:
```
cd pynca

pip install -e .
```

### Usage Guide

#### Generating dummy data

Once installed, PyNCA includes functionality to create "dummy" PK datasets using the *pk_dummy_data* class. These dummy data are intended to provide the user with a dataset for testing the main functionality of PyNCA offered in the *pk_data* class. 

To create a dummy dataset, enter the ```--generate``` argument. If no additional arguments are entered, the system will prompt the user to provide additional arguments, including:

- ```--dummy_n_ids```: the number of unique individuals
- ```--dummy_times```: the "sampling time" to include (as a space-separated *list*)
- ```--dummy_dose```: a single dose at TIME == 0
- ```--dummy_half_life```: a *float* value to generate the approximate concentration-time trends

An example of a full call to *pk_dummy_data* is shown below:
```
python -m pynca --generate --dummy_n_ids 10 --dummy_times 0 0.5 1 2 6 12 24 48 72 168 --dummy_dose 100 --dummy_half_life 12
```

Once generated, the dummy data are saved in the same directory as the package with the filename **pk_dummy_iv_bolus_1cmt.csv**.

### Data format

Analysis can be performed on the dummy data or actual PK data; the only requirement is that **the column names must be correctly provided**. Note that the current iteration of PyNCA only accepts a single bolus dose given at TIME ==0. An example dataset is shown below:

|ID |TIME|CONC |DOSE|
|--:|---:|----:|---:|
|1  | 0  | 95.5| 100|
|1  | 0.5| 80.1|   0|
|1  |   1| 72.2|   0|
|2  | 0  | 98.0| 100|
|2  | 0.5| 79.7|   0|
|2  |   1| 74.8|   0|
|...|....|.....|....|  
| 10|   1| 70.9|   0|

Additional data columns will be ignored.

#### Summarizing the PK data

PyNCA includes functionality to analyze the provided PK data via the ```--summarize``` command. If requested, the data will be summarized by mean, SD, median, minimum, and maximum for each time point.

The following code performs the summarization and prints the results in the command line interface:

```
python -m pynca -f "pk_dummy_iv_bolus_1cmt.csv" --summarize
```

#### Plotting the data

The raw PK data can be plotted, either with or without summarization, via the ```--plot``` command. Plots are created via the *plotly* package, allowing them to be interactive. To take advantage of this interactivity, plots are exported to HTML files with the name "pk_plot.html". They can be viewed using a browser. 

The following code will generate a plot file (without summarization and on a semi-log scale):

```
python -m pynca -f "pk_dummy_iv_bolus_1cmt.csv" --plot --log_scale
```

#### Performing an NCA

The data can be provided to PyNCA via the ```--file``` argument, which takes a *string* filepath. The data are imported and analyzed in a single call, for example:

```
python -m pynca -f "pk_dummy_iv_bolus_1cmt.csv" --nca --auc_start 0 --auc_end 168 --terminal_times 24 48 72
```

The code above calls ```pynca``` and loads the file via ```-f```. Next, the user can perform an NCA using ```--nca```, which requires the arguments ```--auc_start```, ```--auc_end```, and ```--terminal_times```. Together, this command will calculate the following parameters:

- Maximum concentration (C~max~)
- Time to C~max~ (T~max~)
- Half-life (t~1/2~)
- Volume of distribution (V~d~)
- Clearance rate (CL)
- Area under the concentration-time curve (AUC)

*Note that AUC~0-infinity~ is not supported at this time.*

The report can be saved to a text file using the following command:
```
python -m pynca -f "pk_dummy_iv_bolus_1cmt.csv" --nca --auc_start 0 --auc_end 168 --terminal_times 24 48 72 --report "NCA_report.txt"
```

#### Additional details

The PyNCA package contains additional functions in the *pk_data* class that are not readily accessible from the command line. These functions are implicitly called via the *report* function; however, future iterations of the package will add functionality to call these functions directly and specify which statistics to include.

### Limitations

PyNCA is currently only set up to perform simple NCAs on data that include a single dose given at TIME == 0. Additionally, the AUC function only accepts a single start time and a single end time, meaning that the user will need to call the function separately if exploring different regions of the concentration-time curve.

The dummy data generation available in the *pk_dummy_data* class currently can only generate data consistent with PK trends seen in IV bolus with a single compartment. Note that the NCA methods are not limited to this type of data.

### Disclaimer

PyNCA is provided **as-is** without any claims as to its reliability or validity. PyNCA is intended to function as a **proof-of-concept** and should not be used on any preclinical or clinical data at this time. The author accepts **no liability** for misuse of this package or the included functions. 

