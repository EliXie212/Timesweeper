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

cnn_preds = pd.read_csv(
    "/pine/scr/l/s/lswhiteh/timeSeriesSweeps/onePop-selectiveSweep-20Samp-10Int/TimeSweeperSHIC_predictions.csv",
    header=0,
)
rawIDs = list(cnn_preds["id"])
rawIDs = [i.replace("batch", "") for i in rawIDs]
rawIDs = [i.replace("rep_", "") for i in rawIDs]
cleanIDs = [i.split("_") for i in rawIDs]

data_dir = (
    "/pine/scr/l/s/lswhiteh/timeSeriesSweeps/onePop-selectiveSweep-20Samp-10Int/sims/"
)


samp_dict = {
    "file": [],
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

for i in tqdm(
    [
        os.path.join(data_dir, j[0], "muts", "_".join([j[0], j[1]]), j[2] + ".muts.fit")
        for j in cleanIDs
    ],
    desc="Filling dictionary...",
):
    try:
        fit_df = pd.read_csv(i, header=0).dropna().reset_index()
    except FileNotFoundError:
        print(i, "doesn't exist. Passing.")
        continue

    fit_df["window"] = fit_df["window"].astype(int)

    for win in pd.unique(fit_df["window"]):
        samp_dict["file"].append(i)

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