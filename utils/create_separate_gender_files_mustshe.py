import numpy as np
import json
import sys
import os
import argparse
import re
import random
import json

random.seed(0)

parser = argparse.ArgumentParser(description='create_separate_gender_files_mustshe.py')
parser.add_argument('-raw_path', required=True, default=None)
parser.add_argument('-json_path', required=True, default=None)

def main():

    opt = parser.parse_args()
    raw_path = opt.raw_path

    for ref in ["correct_ref", "wrong_ref"]:
        for gender in ["feminine", "masculine"]:
            for f in os.listdir(f"{raw_path}/{ref}"):
                if f.endswith(".s"):
                    lset = os.path.basename(f)[:5]
                    sl = lset.split("-")[0]
                    tl = lset.split("-")[1]

                    src_in = open(f"{raw_path}/{ref}/{lset}.s", "r", encoding="utf-8")
                    tgt_in = open(f"{raw_path}/{ref}/{lset}.t", "r", encoding="utf-8")

                    src_out = open(f"{raw_path}/{ref}/{gender}/{lset}.s", "w", encoding="utf-8")     
                    tgt_out = open(f"{raw_path}/{ref}/{gender}/{lset}.t", "w", encoding="utf-8")     

                    if tl != "en":
                        g_lan = tl
                    else:
                        g_lan = sl

                    category_in = open(f"{raw_path}/{ref}/{g_lan}_category.csv", "r", encoding="utf-8")
                    speaker_in = open(f"{raw_path}/{ref}/{g_lan}_speaker.csv", "r", encoding="utf-8")
                    gterms_in = open(f"{raw_path}/{ref}/{g_lan}_gterms.csv", "r", encoding="utf-8")

                    category_out = open(f"{raw_path}/{ref}/{gender}/annotation/{g_lan}_category.csv", "w", encoding="utf-8")
                    speaker_out = open(f"{raw_path}/{ref}/{gender}/annotation/{g_lan}_speaker.csv", "w", encoding="utf-8")
                    gterms_out = open(f"{raw_path}/{ref}/{gender}/annotation/{g_lan}_gterms.csv", "w", encoding="utf-8")

                    for src, tgt, ctg, spk, gtm in zip(src_in, tgt_in, category_in, speaker_in, gterms_in):
                        gender_word_forms = ctg[1]
                        if (gender_word_forms == "F" and gender == "feminine") or (gender_word_forms == "M" and gender == "masculine"):
                                src_out.write(src)
                                tgt_out.write(tgt)
                                category_out.write(ctg)
                                speaker_out.write(spk)
                                gterms_out.write(gtm)
                        else:
                            continue


def main_equal_f_m_instances():
    opt = parser.parse_args()
    raw_path = opt.raw_path
    jason_path = opt.json_path

    for ref in ["correct_ref", "wrong_ref"]:
        for f in os.listdir(f"{raw_path}/{ref}"):
            if f.endswith(".s"):
                lset = os.path.basename(f)[:5]
                sl = lset.split("-")[0]
                tl = lset.split("-")[1]

                src_in = open(f"{raw_path}/{ref}/{lset}.s", "r", encoding="utf-8")
                tgt_in = open(f"{raw_path}/{ref}/{lset}.t", "r", encoding="utf-8")

                f_src_out = open(f"{raw_path}/{ref}/feminine/{lset}.s", "w", encoding="utf-8")     
                f_tgt_out = open(f"{raw_path}/{ref}/feminine/{lset}.t", "w", encoding="utf-8")     
                m_src_out = open(f"{raw_path}/{ref}/masculine/{lset}.s", "w", encoding="utf-8")     
                m_tgt_out = open(f"{raw_path}/{ref}/masculine/{lset}.t", "w", encoding="utf-8")     
                all_src_out = open(f"{raw_path}/{ref}/all/{lset}.s", "w", encoding="utf-8")     
                all_tgt_out = open(f"{raw_path}/{ref}/all/{lset}.t", "w", encoding="utf-8")     

                if tl != "en":
                    g_lan = tl
                else:
                    g_lan = sl

                category_in = open(f"{raw_path}/{ref}/{g_lan}_category.csv", "r", encoding="utf-8")
                speaker_in = open(f"{raw_path}/{ref}/{g_lan}_speaker.csv", "r", encoding="utf-8")
                gterms_in = open(f"{raw_path}/{ref}/{g_lan}_gterms.csv", "r", encoding="utf-8")

                f_category_out = open(f"{raw_path}/{ref}/feminine/annotation/{g_lan}_category.csv", "w", encoding="utf-8")
                f_speaker_out = open(f"{raw_path}/{ref}/feminine/annotation/{g_lan}_speaker.csv", "w", encoding="utf-8")
                f_gterms_out = open(f"{raw_path}/{ref}/feminine/annotation/{g_lan}_gterms.csv", "w", encoding="utf-8")

                m_category_out = open(f"{raw_path}/{ref}/masculine/annotation/{g_lan}_category.csv", "w", encoding="utf-8")
                m_speaker_out = open(f"{raw_path}/{ref}/masculine/annotation/{g_lan}_speaker.csv", "w", encoding="utf-8")
                m_gterms_out = open(f"{raw_path}/{ref}/masculine/annotation/{g_lan}_gterms.csv", "w", encoding="utf-8")
                
                all_category_out = open(f"{raw_path}/{ref}/all/annotation/{g_lan}_category.csv", "w", encoding="utf-8")
                all_speaker_out = open(f"{raw_path}/{ref}/all/annotation/{g_lan}_speaker.csv", "w", encoding="utf-8")
                all_gterms_out = open(f"{raw_path}/{ref}/all/annotation/{g_lan}_gterms.csv", "w", encoding="utf-8")

                f = {
                    "src": [],
                    "tgt": [],
                    "ctg": [],
                    "spk": [],
                    "gtm": []
                }

                m = {
                    "src": [],
                    "tgt": [],
                    "ctg": [],
                    "spk": [],
                    "gtm": []
                }

                all = {
                    "src": [],
                    "tgt": [],
                    "ctg": [],
                    "spk": [],
                    "gtm": []
                }

                for src, tgt, ctg, spk, gtm in zip(src_in, tgt_in, category_in, speaker_in, gterms_in):
                    gender_word_forms = ctg[1]
                    if gender_word_forms == "F":
                        if "1" in ctg or "2" in ctg:  # disregard cat. 3 and 4
                            if "She\n" == spk or "He\n" == spk: # disregard Mixes
                                f["src"].append(src)
                                f["tgt"].append(tgt)
                                f["ctg"].append(ctg)
                                f["spk"].append(spk)
                                f["gtm"].append(gtm)

                    if gender_word_forms == "M":
                        if "1" in ctg or "2" in ctg:  # disregard cat. 3 and 4
                            if "She\n" == spk or "He\n" == spk: # disregard Mixes
                                m["src"].append(src)
                                m["tgt"].append(tgt)
                                m["ctg"].append(ctg)
                                m["spk"].append(spk)
                                m["gtm"].append(gtm)

                equal_num_instances = min(len(f["src"]), len(m["src"]))
                unbalance_factor = 0.05
                n_f = 0
                n_m = 0
                if len(f["src"]) > len(m["src"]):
                    n_f = int(equal_num_instances * (1 + unbalance_factor))
                    n_m = equal_num_instances
                elif len(f["src"]) < len(m["src"]):
                    n_f = equal_num_instances
                    n_m = int(equal_num_instances * (1 + unbalance_factor))
                else:
                    n_f = equal_num_instances
                    n_m = equal_num_instances 

                f_indices = list(range(len(f["src"])))
                # random.shuffle(f_indices)
                f_indices = f_indices[:n_f]

                m_indices = list(range(len(m["src"])))
                # random.shuffle(m_indices)
                m_indices = m_indices[:n_m]

                # dataset statistics
                stats = {

                    "n_feminine": 0,
                    "n_feminine_female": 0,
                    "n_feminine_male": 0,
                    "n_feminine_1": 0,
                    "n_feminine_1_female": 0,
                    # "n_feminine_1_male": 0,
                    "n_feminine_2": 0,
                    "n_feminine_2_female": 0,
                    "n_feminine_2_male": 0,

                    "n_masculine": 0,
                    "n_masculine_female": 0,
                    "n_masculine_male": 0,
                    "n_masculine_1": 0,
                    # "n_masculine_1_female": 0,
                    "n_masculine_1_male": 0,
                    "n_masculine_2": 0,
                    "n_masculine_2_female": 0,
                    "n_masculine_2_male": 0,
                
                    "n_1": 0,
                    "n_2": 0
                }

                for i in f_indices:
                    f_src_out.write(f["src"][i])
                    f_tgt_out.write(f["tgt"][i])
                    f_category_out.write(f["ctg"][i])
                    f_speaker_out.write(f["spk"][i])
                    f_gterms_out.write(f["gtm"][i])

                    all["src"].append(f["src"][i])
                    all["tgt"].append(f["tgt"][i])
                    all["ctg"].append(f["ctg"][i])
                    all["spk"].append(f["spk"][i])
                    all["gtm"].append(f["gtm"][i])

                    if "1" in f["ctg"][i]:
                        if "She\n" == f["spk"][i]:
                            stats["n_feminine_1_female"] += 1
                            stats["n_feminine_female"] += 1
                        else:
                            stats["n_feminine_1_male"] += 1
                            stats["n_feminine_male"] += 1
                        stats["n_feminine_1"] += 1
                        stats["n_1"] += 1
                    else:
                        if "She\n" == f["spk"][i]:
                            stats["n_feminine_2_female"] += 1
                            stats["n_feminine_female"] += 1
                        else:
                            stats["n_feminine_2_male"] += 1
                            stats["n_feminine_male"] += 1
                        stats["n_feminine_2"] += 1
                        stats["n_2"] += 1

                    stats["n_feminine"] += 1

                for i in m_indices:
                    m_src_out.write(m["src"][i])
                    m_tgt_out.write(m["tgt"][i])
                    m_category_out.write(m["ctg"][i])
                    m_speaker_out.write(m["spk"][i])
                    m_gterms_out.write(m["gtm"][i])

                    all["src"].append(m["src"][i])
                    all["tgt"].append(m["tgt"][i])
                    all["ctg"].append(m["ctg"][i])
                    all["spk"].append(m["spk"][i])
                    all["gtm"].append(m["gtm"][i])

                    if "1" in m["ctg"][i]:
                        if "She\n" == m["spk"][i]:
                            stats["n_masculine_1_female"] += 1
                            stats["n_masculine_female"] += 1
                        else:
                            stats["n_masculine_1_male"] += 1
                            stats["n_masculine_male"] += 1
                        stats["n_masculine_1"] += 1
                        stats["n_1"] += 1
                    else:
                        if "She\n" == m["spk"][i]:
                            stats["n_masculine_2_female"] += 1
                            stats["n_masculine_female"] += 1
                        else:
                            stats["n_masculine_2_male"] += 1
                            stats["n_masculine_male"] += 1
                        stats["n_masculine_2"] += 1
                        stats["n_2"] += 1

                    stats["n_masculine"] += 1

                # export dataset stats
                with open(f"{jason_path}/mustshe_stats.json", 'w') as file:
                    file.write(json.dumps(stats, indent=3))

                for src, tgt, ctg, spk, gtm in zip(all["src"], all["tgt"], all["ctg"], all["spk"], all["gtm"]):
                    all_src_out.write(src)
                    all_tgt_out.write(tgt)
                    all_category_out.write(ctg)
                    all_speaker_out.write(spk)
                    all_gterms_out.write(gtm)


if __name__ == '__main__':
    # main()
    main_equal_f_m_instances()
