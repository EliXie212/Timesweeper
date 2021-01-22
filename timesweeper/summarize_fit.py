import numpy as np
from glob import glob
import os
from tqdm import tqdm
import pandas as pd

"""
- Take max and avg for FIT values in window
- Bin muts by 11 subwindows, m2 is in the center window
- 3 ROC curves: max across subwindows, mean, just true selected site

mut_ID,mut_type,location,window,fit_t,fit_p,selection_detected
79842,m1,45009,4,-1.6735540243396543,0.12006366972163422,0
"""


"""
Ask Dan about how to handle mean/pval/etc
"""

data_dir = "/pine/scr/l/s/lswhiteh/timeSeriesSweeps/onePop-selectiveSweep-20Samp-10Int/sims/*/muts/*"
samp_dict = {
    "window": [],
    "min_p_val": [],
    "min_p_soft": [],
    "min_p_hard": [],
    "mean": [],
    "mean_detect_soft": [],
    "mean_detect_hard": [],
    "true_site_soft": [],
    "true_site_hard": [],
}

for i in tqdm(glob(os.path.join(data_dir, "*fit")), desc="Filling dictionary..."):
    fit_df = pd.read_csv(i, header=0).dropna().reset_index()

    fit_df["window"] = fit_df["window"].astype(int)

    for win in pd.unique(fit_df["window"]):
        win_sub = fit_df[fit_df["window"] == win]
        samp_dict["window"].append(win)
        samp_dict["min_p_val"].append(np.min(win_sub["fit_p"]))

        if samp_dict["min_p_val"][-1] <= 0.005:
            samp_dict["min_p_hard"].append(1)  # hard
            samp_dict["min_p_soft"].append(0)
        elif (samp_dict["min_p_val"][-1] <= 0.05) and (
            samp_dict["min_p_val"][-1] > 0.005
        ):
            samp_dict["min_p_hard"].append(0)  # soft
            samp_dict["min_p_soft"].append(1)
        else:
            samp_dict["min_p_hard"].append(0)
            samp_dict["min_p_soft"].append(0)

        samp_dict["mean"].append(np.mean(win_sub["fit_p"]))
        if samp_dict["mean"][-1] <= 0.005:
            samp_dict["mean_detect_hard"].append(1)  # hard
            samp_dict["mean_detect_soft"].append(0)
        elif (samp_dict["mean"][-1] <= 0.05) and (samp_dict["mean"][-1] > 0.005):
            samp_dict["mean_detect_hard"].append(0)  # soft
            samp_dict["mean_detect_soft"].append(1)
        else:
            samp_dict["mean_detect_hard"].append(0)
            samp_dict["mean_detect_soft"].append(0)

        if "hard" in i and "m2" in list(win_sub["mut_type"]):
            samp_dict["true_site_hard"].append(1)
            samp_dict["true_site_soft"].append(0)
        elif "soft" in i and "m2" in list(win_sub["mut_type"]):
            samp_dict["true_site_hard"].append(0)
            samp_dict["true_site_soft"].append(1)
        else:
            samp_dict["true_site_hard"].append(0)
            samp_dict["true_site_soft"].append(0)

final_df = pd.DataFrame(samp_dict)
final_df.to_csv("sample_dict.csv", header=True, index=False)