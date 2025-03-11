#!/usr/bin/env python

"""
Command line interface to PyNCA
"""

import pandas as pd
import plotly.express as px
import numpy as np
from scipy.stats import linregress

class pk_dummy_data:
    def __init__(self, n_ids:int, times:list, dose:list):
        self.n_ids = n_ids
        self.times = times
        self.dose = dose

        self.len_times = len(times)

        if len(dose) != 1:
            raise Exception(f"Only a single dose can be entered; {len(dose)} provided.")
    
        time_seq = np.array(times)
        dose_seq = np.array(dose)
        self.time_seq = time_seq

        while len(dose_seq) < self.len_times:
            dose_seq = np.append(dose_seq, 0)

        id_col = np.repeat(np.arange(1, n_ids + 1), self.len_times)
        time_col = np.tile(time_seq, n_ids)
        dose_col = np.tile(dose_seq, n_ids)

        self.df = pd.DataFrame({
            "ID": id_col,
            "TIME": time_col,
            "DOSE": dose_col
        })

    def iv_bolus_1cmt(self, half_life:float):
        k = np.log(2) / half_life  # Elimination rate constant
        C0 = self.dose  # Initial concentration

        conc_trend = C0 * np.exp(-k * self.time_seq)

        conc_data = []
        for _ in range(self.n_ids):
            variability = np.random.normal(1, 0.05, size=len(conc_trend))
            variability = np.clip(variability, 0.9, 1.1)
            conc = np.round(conc_trend * variability, 2)

            # Ensure concentrations consistently decrease
            conc_monotonic = [conc[0]]
            for val in conc[1:]:
                conc_monotonic.append(min(conc_monotonic[-1], val))

            conc_data.extend(conc_monotonic)

        self.df = self.df.assign(TREND=np.tile(np.round(conc_trend, 2), self.n_ids))
        self.df["CONC"] = conc_data

        return self.df

class pk_data:
    def __init__(self, df:pd.DataFrame):
        '''Initialize the pk_data object'''
        self.df = df

        df["ID"] = df["ID"].astype(int)
        df["TIME"] = df["TIME"].astype(float)
        df["DOSE"] = df["DOSE"].astype(float)
        df["CONC"] = df["CONC"].astype(float)

        self.list_ids = self.df['ID'].unique()

    def summarize(self):
        summ = self.df.groupby('TIME')['CONC'].agg(["count", "mean", "std", "median", "min", "max"]).reset_index()
        return summ
        
    def summ_stats(self, vals:list, stat=['mean', 'sd', 'min', 'max', 'Q1', 'median', 'Q3', 'IQR']):
        # Ensures user requests valid stats
        for i in stat:
            if i not in self.stat_list:
                raise Exception("""Unsupported statistic. Please enter an array of one or more of 'mean', 'sd', 'min', 'max', 'Q1', 'median', 'Q3', or 'IQR'.
               Leave blank to calculate all statistics.""")
    
        vals_series = pd.Series(vals)
    
        stats = {
                'mean': vals_series.mean(),
                'sd': vals_series.std(),
                'min': vals_series.min(),
                'max': vals_series.max(),
                'Q1': vals_series.quantile(0.25),
                'median': vals_series.median(),
                'Q3': vals_series.quantile(0.75),
                'IQR': vals_series.quantile(0.75) - vals_series.quantile(0.25)
        }
    
        stats = {k: v for k, v in stats.items() if k in stat}   
    
        return pd.DataFrame([stats])

    def half_life(self, term_elim_times:list, stat=['mean', 'sd', 'min', 'max', 'Q1', 'median', 'Q3', 'IQR']):
        half_lives = []
        for ID in self.list_ids:
            subset = self.df.loc[self.df['ID'] == ID]
            ln_conc = np.log(subset['CONC'])
            slope, _, r_value, _, _ = linregress(subset['TIME'], ln_conc)
            if slope >= 0:
                continue  # biologically invalid slope, skip
            half_life = np.log(2) / -slope
            half_lives.append(half_life)
        return self.summ_stats(half_lives, stat=stat)

    def cmax(self, stat=['mean', 'sd', 'min', 'max', 'Q1', 'median', 'Q3', 'IQR']):
        cmax_vals = self.df.groupby('ID')['CONC'].max()
        return self.summ_stats(cmax_vals, stat=stat)

    def tmax(self, stat=['mean', 'sd', 'min', 'max', 'Q1', 'median', 'Q3', 'IQR']):
        tmax_vals = []
        for ID in self.list_ids:
            subset = self.df.loc[self.df['ID'] == ID]
            tmax = subset.loc[subset['CONC'] == subset['CONC'].max()]['TIME'].iloc[0]
            tmax_vals.append(tmax)
        return self.summ_stats(tmax_vals, stat=stat)

    def auc(self, start:int, end:int, stat=['mean', 'sd', 'min', 'max', 'Q1', 'median', 'Q3', 'IQR'], ind=False):
        auc_vals = []
        for ID in self.list_ids:
            subset_id = self.df.loc[self.df['ID'] == ID]
            subset_time = subset_id[(subset_id['TIME'] >= start) & (subset_id['TIME'] <= end)]
            auc = np.trapezoid(subset_time['CONC'], subset_time['TIME'])
            auc_vals.append(auc)

        if ind:
            return auc_vals
        else:
            return self.summ_stats(auc_vals, stat=stat)

    def vd(self, stat=['mean', 'sd', 'min', 'max', 'Q1', 'median', 'Q3', 'IQR'], silence_message=False):
        if not silence_message:
            print("NB: The current iteration of 'vd()' only works for a single bolus dose given at 'TIME' == 0.")
        
        vd_vals = []
        for ID in self.list_ids:
            subset = self.df.loc[(self.df['ID'] == ID) & (self.df['TIME'] == 0)]
            dose = subset['DOSE'].iloc[0]
            c0 = subset['CONC'].iloc[0]
            vd = dose / c0
            vd_vals.append(vd)
        return self.summ_stats(vd_vals, stat=stat)

    def cl(self, start, end, stat=['mean', 'sd', 'min', 'max', 'Q1', 'median', 'Q3', 'IQR'], silence_message=False):
        if not silence_message:
            print("NB: The current iteration of 'cl()' only works for a single bolus dose given at 'TIME' == 0.")
            
        subset = self.df.loc[self.df['DOSE'] != 0].copy().reset_index()
        auc = self.auc(start=start, end=end, ind=True)
        cl_vals = subset['DOSE'] / auc
        return self.summ_stats(cl_vals, stat=stat)
    
    def plot(self, summarized=False, log_scale=False):
        if summarized:
            summary = self.summarize()
            fig = px.line(summary, x="TIME", y="mean", error_y="std", markers=True, log_y=log_scale,
                          title="Mean (SD) PK concentration profile")
        else:
            fig = px.line(self.df, x="TIME", y="CONC", color="ID", markers=True, log_y=log_scale,
                          title="Individual PK concentration profiles")
        
        fig.update_layout(xaxis_title="Time", yaxis_title="Concentration")
        fig.show()

    def report(self, term_elim_times:list, start, end):
        print(f"Summary of PK data: \n{self.summarize()}\n\n")
        print(f"Cmax: \n{self.cmax()}\n\n")
        print(f"Tmax: \n{self.tmax()}\n\n")
        print(f"t1/2: \n{self.half_life(term_elim_times=term_elim_times)}\n\n")
        print(f"AUC({start}-{end}): \n{self.auc(start=start, end = end)}\n\n")
        print(f"Vd: \n{self.vd(silence_message=True)}\n\n")
        print(f"CL: \n{self.cl(start=start, end = end, silence_message=True)}\n\n")