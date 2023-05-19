import numpy as np
import pandas as pd
import json
import pickle
import argparse

parser = argparse.ArgumentParser(description='create_results_data_frames.py')
parser.add_argument('-in_path', required=True, default=None)
parser.add_argument('-out_path', required=True, default=None)

def create_data_frames():

    opt = parser.parse_args()
    in_path = opt.in_path
    out_path = opt.out_path

    df_bleu = pd.read_excel(f"{in_path}/df_bleu.xlsx")
    df_acc_cat = pd.read_excel(f"{in_path}/df_acc_cat.xlsx")
    df_acc_speaker = pd.read_excel(f"{in_path}/df_acc_speaker.xlsx")

    names_bleu = {
        "Unnamed: 0": "sl",
        "Unnamed: 1": "tl",
        "Unnamed: 2": "model",
        "All": "all_cor_zs",
        "Unnamed: 4": "all_cor_pv",
        "Unnamed: 5": "all_wro_zs",
        "Unnamed: 6": "all_wro_pv",
        "Unnamed: 7": "all_diff_zs",
        "Unnamed: 8": "all_diff_pv",
        "Unnamed: 9": "all_sum_diff_zs",
        "Unnamed: 10": "all_sum_diff_pv",
        "Feminine": "f_cor_zs",
        "Unnamed: 12": "f_cor_pv",
        "Unnamed: 13": "f_wro_zs",
        "Unnamed: 14": "f_wro_pv",
        "Unnamed: 15": "f_diff_zs",
        "Unnamed: 16": "f_diff_pv",
        "Unnamed: 17": "f_sum_diff_zs",
        "Unnamed: 18": "f_sum_diff_pv",
        "Masculine": "m_cor_zs",
        "Unnamed: 20": "m_cor_pv",
        "Unnamed: 21": "m_wro_zs",
        "Unnamed: 22": "m_wro_pv",
        "Unnamed: 23": "m_diff_zs",
        "Unnamed: 24": "m_diff_pv",
        "Unnamed: 25": "m_sum_diff_zs",
        "Unnamed: 26": "m_sum_diff_pv",
        "Additional": "f_of_cor_zs",
        "Unnamed: 28": "m_of_cor_zs",
        "Unnamed: 29": "diff_f_m_of_cor_zs",
        "Unnamed: 30": "f_of_cor_pv",
        "Unnamed: 31": "m_of_cor_pv",
        "Unnamed: 32": "diff_f_m_of_cor_pv",
        "Unnamed: 33": "gatq_zs",
        "Unnamed: 34": "gatq_pv",
    }
    names_acc_cat = {
        "Unnamed: 0": "sl",
        "Unnamed: 1": "tl",
        "Unnamed: 2": "model",
        "Unnamed: 3": "category",
        "All": "all_cor_zs",
        "Unnamed: 5": "all_cor_pv",
        "Unnamed: 6": "all_wro_zs",
        "Unnamed: 7": "all_wro_pv",
        "Unnamed: 8": "all_diff_zs",
        "Unnamed: 9": "all_diff_pv",
        "Unnamed: 10": "all_sum_diff_zs",
        "Unnamed: 11": "all_sum_diff_pv",
        "Feminine": "f_cor_zs",
        "Unnamed: 13": "f_cor_pv",
        "Unnamed: 14": "f_wro_zs",
        "Unnamed: 15": "f_wro_pv",
        "Unnamed: 16": "f_diff_zs",
        "Unnamed: 17": "f_diff_pv",
        "Unnamed: 18": "f_sum_diff_zs",
        "Unnamed: 19": "f_sum_diff_pv",
        "Masculine": "m_cor_zs",
        "Unnamed: 21": "m_cor_pv",
        "Unnamed: 22": "m_wro_zs",
        "Unnamed: 23": "m_wro_pv",
        "Unnamed: 24": "m_diff_zs",
        "Unnamed: 25": "m_diff_pv",
        "Unnamed: 26": "m_sum_diff_zs",
        "Unnamed: 27": "m_sum_diff_pv",
        "Additional": "f_of_cor_zs",
        "Unnamed: 29": "m_of_cor_zs",
        "Unnamed: 30": "diff_f_m_of_cor_zs",
        "Unnamed: 31": "f_of_cor_pv",
        "Unnamed: 32": "m_of_cor_pv",
        "Unnamed: 33": "diff_f_m_of_cor_pv",
        "Unnamed: 34": "gatq_zs",
        "Unnamed: 35": "gatq_pv",
    }

    names_acc_speaker = {
        "Unnamed: 0": "sl",
        "Unnamed: 1": "tl",
        "Unnamed: 2": "model",
        "Unnamed: 3": "speaker",
        "All": "all_cor_zs",
        "Unnamed: 5": "all_cor_pv",
        "Unnamed: 6": "all_wro_zs",
        "Unnamed: 7": "all_wro_pv",
        "Unnamed: 8": "all_diff_zs",
        "Unnamed: 9": "all_diff_pv",
        "Unnamed: 10": "all_sum_diff_zs",
        "Unnamed: 11": "all_sum_diff_pv",
        "Feminine": "f_cor_zs",
        "Unnamed: 13": "f_cor_pv",
        "Unnamed: 14": "f_wro_zs",
        "Unnamed: 15": "f_wro_pv",
        "Unnamed: 16": "f_diff_zs",
        "Unnamed: 17": "f_diff_pv",
        "Unnamed: 18": "f_sum_diff_zs",
        "Unnamed: 19": "f_sum_diff_pv",
        "Masculine": "m_cor_zs",
        "Unnamed: 21": "m_cor_pv",
        "Unnamed: 22": "m_wro_zs",
        "Unnamed: 23": "m_wro_pv",
        "Unnamed: 24": "m_diff_zs",
        "Unnamed: 25": "m_diff_pv",
        "Unnamed: 26": "m_sum_diff_zs",
        "Unnamed: 27": "m_sum_diff_pv",
        "Additional": "f_of_cor_zs",
        "Unnamed: 29": "m_of_cor_zs",
        "Unnamed: 30": "diff_f_m_of_cor_zs",
        "Unnamed: 31": "f_of_cor_pv",
        "Unnamed: 32": "m_of_cor_pv",
        "Unnamed: 33": "diff_f_m_of_cor_pv",
        "Unnamed: 34": "gatq_zs",
        "Unnamed: 35": "gatq_pv",
    }

    df_bleu = df_bleu.rename(columns=names_bleu)
    df_acc_cat = df_acc_cat.rename(columns=names_acc_cat)
    df_acc_speaker = df_acc_speaker.rename(columns=names_acc_cat)

    with open(f"{out_path}/df_bleu.pkl", "wb") as file:
        pickle.dump(df_bleu, file)

    with open(f"{out_path}/df_acc.pkl", "wb") as file:
        pickle.dump(df_bleu, file)

    with open(f"{out_path}/df_acc_cat.pkl", "wb") as file:
        pickle.dump(df_acc_cat, file)

    with open(f"{out_path}/df_acc_speaker.pkl", "wb") as file:
        pickle.dump(df_acc_speaker, file)


if __name__ == "__main__":
    create_data_frames()