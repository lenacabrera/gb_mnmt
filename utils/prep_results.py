import numpy as np
import json
import sys
import os
import argparse
import re
import pandas as pd
import pickle
import os
import nltk
from torchmetrics import SacreBLEUScore
from nltk.translate.bleu_score import SmoothingFunction

import warnings
warnings.filterwarnings("ignore")
np.seterr('raise')

parser = argparse.ArgumentParser(description='prep_results.py')

parser.add_argument('-raw_path', required=True, default=None)
parser.add_argument('-pred_path', required=True, default=None)
parser.add_argument('-train_set', required=True, default=None)
parser.add_argument('-out_path', required=True, default=None)
parser.add_argument('-out_path_csv', required=True, default=None)
parser.add_argument('-out_path_json', required=True, default=None)
parser.add_argument('-df_path', required=True, default=None)


IDX = 27 # FR: 24, IT: 27, 76, 23 (cause: set accurcay), 103

corrected_references = {
    "es": {},
    "fr": {"Mais unede mes meilleurs amis, un superbe dame kenyan, Esther Kaecha, m'a appelée dans ce moment de désespoir, et elle m'a dit : « Mary, tu as beaucoup de volonté.": "Mais un de mes meilleurs amis, un superbe dame kenyan, Esther Kaecha, m'a appelée dans ce moment de désespoir, et elle m'a dit : « Mary, tu as beaucoup de volonté."},
    "it": {}
}

corrected_gterms = {
    "es": {},
    "fr": {
        "C'était un avocat ou un brasseur d'argent qui, pour le reste de sa vie, pourrait dire aux gens qu'il était entré dans un bâtiment en feu pour sauver une créature vivante, juste parce qu'il m'avait battu de 5 secondes.": "un avocat un brasseur",
        "C'était une avocate ou une brasseuse d'argent qui, pour le reste de sa vie, pourrait dire aux gens qu'il était entré dans un bâtiment en feu pour sauver une créature vivante, juste parce qu'il m'avait battu de 5 secondes.": "une avocate une brasseuse",
    },
    "it": {
        # "Un'altra studentessa ci ha riportato che ha imparato a progettare con empatia, contrariamente al progettare per funzionalità, che era ciò che la sua educazione in ingegneria le aveva insegnato.": "altra studentessa",
        # "Un altro studente ci ha riportato che ha imparato a progettare con empatia, contrariamente al progettare per funzionalità, che era ciò che la sua educazione in ingegneria le aveva insegnato.": "altro studente",
        # "Parlando con un'infermiera il giorno dopo, lei mi disse: \"Oh, parli del menage à trois\".": "infermiera", 
        # "Parlando con un infermiere il giorno dopo, lei mi disse: \"Oh, parli del menage à trois\".": "infermiere", 
        # "E le ho domandato: \"Questo fa di me un'assassina?\" Non ha saputo rispondere.": "assassina", 
        # "E le ho domandato: \"Questo fa di me un assassino?\" Non ha saputo rispondere.": "assassino", 
        # "Il suo nome è Dottor Pizzutillo, un Italoamericano, il cui nome, apparentemente, era troppo difficile da pronunciare per la maggior parte degli americani, così è diventato dottor P. E il dottor P indossava sempre papillon colorati e aveva una perfetta inclinazione per lavorare coi bambini.": "Dottor Italoamericano diventato Dottor Dottor", 
        # "Il suo nome è Dottoressa Pizzutillo, un'Italoamericana, il cui nome, apparentemente, era troppo difficile da pronunciare per la maggior parte degli americani, così è diventata dottoressa P. E il dottoressa P indossava sempre papillon colorati e aveva una perfetta inclinazione per lavorare coi bambini.": "Dottoressa Italoamerican diventata Dottoressa Dottoressa", 
        # "Sono un esperto in relazioni. \"E subito dopo si lancia ancora in discorsi su uccelli rari, alghe e strane piante acquatiche.": "esperto", 
        # "Sono un'esperta in relazioni. \"E subito dopo si lancia ancora in discorsi su uccelli rari, alghe e strane piante acquatiche.": "esperta", 
        },
}


def get_empty_results_dict():
    results = {
        "BLEU": {
            "zero_shot": {
                "all": {
                    "correct_ref": {},
                    "wrong_ref": {},
                    "diff_c_w": {},
                    "sum_c_and_diff_c_w": {},
                },
                "feminine": {
                    "correct_ref": {},
                    "wrong_ref": {},
                    "diff_c_w": {},
                    "sum_c_and_diff_c_w": {},
                },
                "masculine": {
                    "correct_ref": {},
                    "wrong_ref": {},
                    "diff_c_w": {},
                    "sum_c_and_diff_c_w": {},
                },
                "f_of_all_c": {},
                "m_of_all_c": {},
                "diff_f_m_of_all_c": {},
                "tquality_w_gender_performance": {},
            },
            "pivot": {
                "all": {
                    "correct_ref": {},
                    "wrong_ref": {},
                    "diff_c_w": {},
                    "sum_c_and_diff_c_w": {},
                },
                "feminine": {
                    "correct_ref": {},
                    "wrong_ref": {},
                    "diff_c_w": {},
                    "sum_c_and_diff_c_w": {},
                },
                "masculine": {
                    "correct_ref": {},
                    "wrong_ref": {},
                    "diff_c_w": {},
                    "sum_c_and_diff_c_w": {},
                },
                "f_of_all_c": {},
                "m_of_all_c": {},
                "diff_f_m_of_all_c": {},
                "tquality_w_gender_performance": {},
            }
        },
        "accuracy": {
            "zero_shot": {
                "total": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "1": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "2": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "female_speaker": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "male_speaker": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "female_speaker_1": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "female_speaker_2": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "male_speaker_1": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "male_speaker_2": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
            },
            "pivot": {
                "total": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "1": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "2": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "female_speaker": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "male_speaker": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "female_speaker_1": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "female_speaker_2": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "male_speaker_1": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
                "male_speaker_2": {
                    "all": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "feminine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "masculine": {
                        "correct_ref": {},
                        "wrong_ref": {},
                        "diff_c_w": {},
                        "sum_c_and_diff_c_w": {}
                    },
                    "f_of_all_c": {},
                    "m_of_all_c": {},
                    "diff_f_m_of_all_c": {},
                    "tquality_w_gender_performance": {},
                },
            }
        }
    }

    return results

def get_bleu_scores_mustshe(lines):
    bleu_scores = []
    for line in lines:
        if line.split()[0] == "\"score\":":
            bleu_score = re.search(r"[0-9]*.[0-9]*", line.split()[1]).group(0)
            bleu_scores.append(float(bleu_score))
    avg_bleu = round(np.average(np.array(bleu_scores)), 1)
    return avg_bleu

def get_accuracies_mustshe_OLD(raw_path, pred_path, ref, gender_set, f, sl, tl, pl):

    l = tl
    if tl == "en":
        l = sl
    
    gterms_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    if ref == "correct_ref":
        op_gterms_file = open(f"{raw_path}/wrong_ref/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    else:
        op_gterms_file = open(f"{raw_path}/correct_ref/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    speaker_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_speaker.csv", "r", encoding="utf-8")
    category_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_category.csv", "r", encoding="utf-8")
    
    # target reference file (correct/wrong)
    tref_file = open(f"{raw_path}/{ref}/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")

    # swapped "opposite" target reference
    if ref == "correct_ref":
        op_tref_file = open(f"{raw_path}/wrong_ref/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")
    else:
        op_tref_file = open(f"{raw_path}/correct_ref/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")

    # pred file
    if pl == None:
        pred_file = open(f"{pred_path}/{ref}/{gender_set}/{f}", "r", encoding="utf-8")
    else:
        pred_file = open(f"{pred_path}/pivot/{ref}/{gender_set}/{sl}-{pl}-{tl}.real.pivotout.t.pt", "r", encoding="utf-8")

    c_accuracies_total = []
    w_accuracies_total = []
    accuracies_total = []
    accuracies_1 = []
    accuracies_2 = []
    accuracies_f_speaker = []
    accuracies_m_speaker = []
    accuracies_f_speaker_1 = []
    accuracies_f_speaker_2 = []
    accuracies_m_speaker_1 = []
    accuracies_m_speaker_2 = []

    n_pred = []
    n_corr = []
    pred_all = []
    corr_all = []

    c_n_pred = []
    w_n_pred = []
    c_n_corr = []
    w_n_corr = []
    c_pred_all = []
    w_pred_all = []
    c_corr_all = []
    w_corr_all = []

    if tl != "en":
        for j, (tref, op_tref, pred, gterms, op_gterms, speaker, category) in enumerate(zip(tref_file, op_tref_file, pred_file, gterms_file, op_gterms_file, speaker_file, category_file)):
            tref_ = tref.strip()
            op_tref_ = op_tref.strip()
            gterms_list = gterms.split()
            op_gterms_list = op_gterms.split()

            # # correct reference
            # if tref_ in [e.strip() for e in corrected_references[l].keys()]:
            #     tref = corrected_references[l][tref_]
            # if op_tref_ in [e.strip() for e in corrected_references[l].keys()]:
            #     op_tref = corrected_references[l][op_tref_]

            # if tref_ in [e.strip() for e in corrected_gterms[l].keys()]:
            #     # correct gender terms
            #     gterms_list = corrected_gterms[l][tref_].split()
            
            punctuation_marks = [".", ",", "!", "?", ":", ";", "¿", "¡", "\"", "\n", "(", ")", "...", "—", "«", "»"]
            for p_mark in punctuation_marks:
                tref = tref.replace(p_mark, " " + p_mark)
                op_tref = op_tref.replace(p_mark, " " + p_mark)
                pred = pred.replace(p_mark, " " + p_mark)
            tref_list = tref.split()
            op_tref_list = op_tref.split()
            pred_list = pred.split()
             
            # apply upperbound to gender terms, to prevent rewarding over-generated terms
            # gterms_list = list(set(gterms_list))

            keep_expr = ["un", "une", "una", "l", "qu", "J", "j", "d", "D", "n", "N"]
            tref_list_ = []
            for t in tref_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    tref_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            tref_list_.append(st)
                else:
                    tref_list_.append(t)

            op_tref_list_ = []
            for t in op_tref_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    op_tref_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            op_tref_list_.append(st)
                else:
                    op_tref_list_.append(t)

            pred_list_ = []
            for t in pred_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    pred_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            pred_list_.append(st)
                else:
                    pred_list_.append(t)

            tref_list = tref_list_
            op_tref_list = op_tref_list_
            pred_list = pred_list_

            # g_w_indices = []
            # for i, (tw, otw) in enumerate(zip(tref_list, op_tref_list)):
            #     # check where correct and wrong ref. differ and store word index
            #     if tw != otw:
            #         g_w_indices.append(i)

            # # check correct gterm with pred. words ~ gterm pos. idx.
            # n_forward, n_backward = 2, 2  # buffer around orig. gterm pos. idx.
            # pred_gterms = []
            # for i, gterm in enumerate(gterms_list):
            #     pred_all.append(gterm)
            #     if len(g_w_indices) > 0 and i < len(g_w_indices):
            #         idx = g_w_indices[i]
            #         if gterm in pred_list[idx-n_backward:idx+n_forward]:
            #             pred_gterms.append(gterm)
            #             corr_all.append(gterm)
            #     # else:
            #     #     if gterm in pred_list:
            #     #         pred_gterms.append(gterm)

            # Bentivogli et al.
            c_pred_gterms = []
            w_pred_gterms = []
            c_pred_check = pred_list
            w_pred_check = pred_list
            for c_term, w_term in zip(gterms_list, op_gterms_list):
                c_pred_all.append(c_term)
                w_pred_all.append(w_term)
                if c_term in c_pred_check:
                    c_pred_gterms.append(c_term)
                    c_corr_all.append(c_term)
                    for k in range(len(c_pred_check)):
                        if c_pred_check[k] == c_term:
                            del c_pred_check[k]
                            break

                if w_term in w_pred_check:
                    w_pred_gterms.append(w_term)
                    w_corr_all.append(w_term)
                    for k in range(len(w_pred_check)):
                        if w_pred_check[k] == w_term:
                            del w_pred_check[k]
                            break

            # compute accuracy
            c_acc = len(c_pred_gterms) / len(gterms_list)    
            c_n_pred.append(len(gterms_list))
            c_n_corr.append(len(c_pred_gterms)) 
            w_acc = len(w_pred_gterms) / len(op_gterms_list)    
            w_n_pred.append(len(op_gterms_list))
            w_n_corr.append(len(w_pred_gterms)) 

            # if j == IDX:
            #     # if sl == "it" and tl == "fr":
            #     if sl == "fr" and tl == "it":
            #         print("ACC ref, tref, hyp\n", tref, op_tref, pred)
            #         print(gterms_list)
            #         print(c_pred_gterms)
            #         print(c_acc)
            #         print("---")
            #         print(op_gterms_list)
            #         print(w_pred_gterms)
            #         print(w_acc)
            #         print("===")

            c_accuracies_total.append(c_acc)
            w_accuracies_total.append(w_acc)

            if speaker.replace("\n", "").lower() == "she":
                accuracies_f_speaker.append(c_acc)
            if speaker.replace("\n", "").lower() == "he":
                accuracies_m_speaker.append(c_acc)
            # gender of referred entity
            if "1" in category.replace("\n", ""):
                accuracies_1.append(c_acc)
            if "2" in category.replace("\n", ""):
                accuracies_2.append(c_acc)

            if speaker.replace("\n", "").lower() == "she" and "1" in category.replace("\n", ""):
                accuracies_f_speaker_1.append(c_acc)
            if speaker.replace("\n", "").lower() == "she" and "2" in category.replace("\n", ""):
                accuracies_f_speaker_2.append(c_acc)
            if speaker.replace("\n", "").lower() == "he" and "1" in category.replace("\n", ""):
                accuracies_m_speaker_1.append(c_acc)
            if speaker.replace("\n", "").lower() == "he" and "2" in category.replace("\n", ""):
                accuracies_m_speaker_2.append(c_acc)

        # for k in range(j+1):
        #     accuracies_total.append(len(corr_all)/len(pred_all))

        if len(accuracies_total) == 0:
            accuracies_total.append(0)
        if len(accuracies_1) == 0:
            accuracies_1.append(0)
        if len(accuracies_2) == 0:
            accuracies_2.append(0)
        if len(accuracies_f_speaker) == 0:
            accuracies_f_speaker.append(0)
        if len(accuracies_m_speaker) == 0:
            accuracies_m_speaker.append(0)
        if len(accuracies_f_speaker_1) == 0:
            accuracies_f_speaker_1.append(0)
        if len(accuracies_f_speaker_2) == 0:
            accuracies_f_speaker_2.append(0)
        if len(accuracies_m_speaker_1) == 0:
            accuracies_m_speaker_1.append(0)
        if len(accuracies_m_speaker_2) == 0:
            accuracies_m_speaker_2.append(0)

    return c_accuracies_total, accuracies_1, accuracies_2, accuracies_f_speaker, accuracies_m_speaker, \
        accuracies_f_speaker_1, accuracies_f_speaker_2, accuracies_m_speaker_1, accuracies_m_speaker_2

def get_sentence_bleu_scores_mustshe_OLD(references, hypotheses): #, lset, results):
    i = IDX
    # print("BLEU ref, hyp\n", references[i], hypotheses[i])

    hyps = [h.split() for h in hypotheses]
    refs = [r.split() for r in references]
    refs_corp = [[r.split()] for r in references]

    hps = []
    for h in hyps:
        hs = []
        for w in h:
            if "'" in w:
                a = w.split("'")
                for b in a:
                    hs.append(b)
            else:
                hs.append(w)
        hps.append(hs)

    rps = []
    for r in refs:
        rs = []
        for w in r:
            if "'" in w:
                a = w.split("'")
                for b in a:
                    rs.append(b)
            else:
                rs.append(w)
        rps.append(rs)

    hyps = hps
    refs = rps


    bleu_sent = []
    for j, (reference, hypothesis) in enumerate(zip(refs, hyps)):
        score = nltk.translate.bleu_score.sentence_bleu([reference], hypothesis) * 100
        if j == i:
            print(score)
        #     h = hypothesis

        #     # # FR, idx=24, 'une' idx=38
        #     # r = reference[0][:38] + reference[0][39:]

        #     # IT, idx=28, 'une' idx=40, gterms indices: 15, 16, 18, 19, 20, 22, 25, 32 (22 -> W>C, 23 -> W=C, 24 -> W<C)
        #     # r = reference[0][:23] + reference[0][24:39] + reference[0][40:43] + reference[0][44:]
        #     # print(reference[0][23], reference[0][39], reference[0][43])
            
        #     r = reference[0][:18]
        #     print(r)

        #     # print(SacreBLEUScore(h, [r]))
            print("crop", nltk.translate.bleu_score.sentence_bleu([refs[i]], hyps[i]) * 100)
        #     # print("not crop", nltk.translate.bleu_score.sentence_bleu(reference, hypothesis) * 100)
        
        bleu_sent.append(score)
    # bleu_corp = nltk.translate.bleu_score.corpus_bleu(refs_corp, hyps) * 100
    # print(bleu_corp)

    # # print(references[i][0][:42])
    # # print(hps)
    # bleu_sent = []
    # for j, (reference, hypothesis) in enumerate(zip(references, hypotheses)):
    #     score = nltk.translate.bleu_score.sentence_bleu(reference, hypothesis) * 100
    #     if j == i:
    #         print(score)
    #     #     h = hypothesis

    #     #     # # FR, idx=24, 'une' idx=38
    #     #     # r = reference[0][:38] + reference[0][39:]

    #     #     # IT, idx=28, 'une' idx=40, gterms indices: 15, 16, 18, 19, 20, 22, 25, 32 (22 -> W>C, 23 -> W=C, 24 -> W<C)
    #     #     # r = reference[0][:23] + reference[0][24:39] + reference[0][40:43] + reference[0][44:]
    #     #     # print(reference[0][23], reference[0][39], reference[0][43])
            
    #     #     r = reference[0][:18]
    #     #     print(r)

    #     #     # print(SacreBLEUScore(h, [r]))
    #     #     print("crop", nltk.translate.bleu_score.sentence_bleu([r], h) * 100)
    #     #     # print("not crop", nltk.translate.bleu_score.sentence_bleu(reference, hypothesis) * 100)
        
    #     bleu_sent.append(score)
    # # bleu_corp = nltk.translate.bleu_score.corpus_bleu(references, hypotheses) * 100
    # print(bleu_corp)
    # print(bleu_sent[i])
    # print("BLEU ref, hyp\n", references[i], hypotheses[i])

    return np.array(bleu_sent)

def get_sentence_accuracy_scores_mustshe(raw_path, pred_path, ref, gender_set, f, sl, tl, pl): #, results):
    i = 1
    l = tl
    if tl == "en":
        l = sl
    
    gterms_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    if ref == "correct_ref":
        op_gterms_file = open(f"{raw_path}/wrong_ref/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    else:
        op_gterms_file = open(f"{raw_path}/correct_ref/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    speaker_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_speaker.csv", "r", encoding="utf-8")
    category_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_category.csv", "r", encoding="utf-8")
    
    # target reference file (correct/wrong)
    tref_file = open(f"{raw_path}/{ref}/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")

    # swapped "opposite" target reference
    if ref == "correct_ref":
        op_tref_file = open(f"{raw_path}/wrong_ref/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")
    else:
        op_tref_file = open(f"{raw_path}/correct_ref/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")

    # pred file
    if pl == None:
        pred_file = open(f"{pred_path}/{ref}/{gender_set}/{f}", "r", encoding="utf-8")
    else:
        pred_file = open(f"{pred_path}/pivot/{ref}/{gender_set}/{sl}-{pl}-{tl}.real.pivotout.t.pt", "r", encoding="utf-8")

    accuracies_total = []
    accuracies_1 = []
    accuracies_2 = []
    accuracies_f_speaker = []
    accuracies_m_speaker = []
    accuracies_f_speaker_1 = []
    accuracies_f_speaker_2 = []
    accuracies_m_speaker_1 = []
    accuracies_m_speaker_2 = []

    n_pred = []
    n_corr = []
    pred_all = []
    corr_all = []

    if tl != "en":
        for j, (tref, op_tref, pred, gterms, op_gterms, speaker, category) in enumerate(zip(tref_file, op_tref_file, pred_file, gterms_file, op_gterms_file, speaker_file, category_file)):
            tref_ = tref.strip()
            op_tref_ = op_tref.strip()
            gterms_list = gterms.split()
            op_gterms_list = op_gterms.split()

            # # correct reference
            # if tref_ in [e.strip() for e in corrected_references[l].keys()]:
            #     tref = corrected_references[l][tref_]
            # if op_tref_ in [e.strip() for e in corrected_references[l].keys()]:
            #     op_tref = corrected_references[l][op_tref_]

            # if tref_ in [e.strip() for e in corrected_gterms[l].keys()]:
            #     # correct gender terms
            #     gterms_list = corrected_gterms[l][tref_].split()
            
            punctuation_marks = [".", ",", "!", "?", ":", ";", "¿", "¡", "\"", "\n", "(", ")", "...", "—", "«", "»"]
            for p_mark in punctuation_marks:
                tref = tref.replace(p_mark, " " + p_mark)
                op_tref = op_tref.replace(p_mark, " " + p_mark)
                pred = pred.replace(p_mark, " " + p_mark)
            tref_list = tref.split()
            op_tref_list = op_tref.split()
            pred_list = pred.split()
             
            # apply upperbound to gender terms, to prevent rewarding over-generated terms
            # gterms_list = list(set(gterms_list))

            keep_expr = ["un", "une", "una", "l", "qu", "J", "j", "d", "D", "n", "N"]
            tref_list_ = []
            for t in tref_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    tref_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            tref_list_.append(st)
                else:
                    tref_list_.append(t)

            op_tref_list_ = []
            for t in op_tref_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    op_tref_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            op_tref_list_.append(st)
                else:
                    op_tref_list_.append(t)

            pred_list_ = []
            for t in pred_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    pred_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            pred_list_.append(st)
                else:
                    pred_list_.append(t)

            tref_list = tref_list_
            op_tref_list = op_tref_list_
            pred_list = pred_list_

            g_w_indices = []
            for i, (tw, otw) in enumerate(zip(tref_list, op_tref_list)):
                # check where correct and wrong ref. differ and store word index
                if tw != otw:
                    # if j == IDX:
                    #     print(tw, i)
                    g_w_indices.append(i)

            # check correct gterm with pred. words ~ gterm pos. idx.
            n_forward, n_backward = 2, 2  # buffer around orig. gterm pos. idx.
            pred_gterms = []
            for i, gterm in enumerate(gterms_list):
                pred_all.append(gterm)
                if len(g_w_indices) > 0 and i < len(g_w_indices):
                    idx = g_w_indices[i]
                    # print(pred_list[idx-n_backward:idx+n_forward])
                    if gterm in pred_list[idx-n_backward:idx+n_forward]:
                        pred_gterms.append(gterm)
                        corr_all.append(gterm)
                # else:
                #     if gterm in pred_list:
                #         pred_gterms.append(gterm)

            # Bentivogli et al.
            pred_gterms = []
            for term in gterms_list:
                pred_all.append(term)
                if term in pred_list:
                    pred_gterms.append(term)
                    corr_all.append(term)

            # compute accuracy
            acc = len(pred_gterms) / len(gterms_list)    
            n_pred.append(len(gterms_list))
            n_corr.append(len(pred_gterms)) 

            if j == IDX:
                # if sl == "it" and tl == "fr":
                if sl == "fr" and tl == "it":
                    print("ACC ref, hyp\n", tref, pred)
                    print(gterms_list)
                    print(pred_gterms)
                    print(acc)
                    print("---")

            accuracies_total.append(acc)

            if speaker.replace("\n", "").lower() == "she":
                accuracies_f_speaker.append(acc)
            if speaker.replace("\n", "").lower() == "he":
                accuracies_m_speaker.append(acc)
            # gender of referred entity
            if "1" in category.replace("\n", ""):
                accuracies_1.append(acc)
            if "2" in category.replace("\n", ""):
                accuracies_2.append(acc)

            if speaker.replace("\n", "").lower() == "she" and "1" in category.replace("\n", ""):
                accuracies_f_speaker_1.append(acc)
            if speaker.replace("\n", "").lower() == "she" and "2" in category.replace("\n", ""):
                accuracies_f_speaker_2.append(acc)
            if speaker.replace("\n", "").lower() == "he" and "1" in category.replace("\n", ""):
                accuracies_m_speaker_1.append(acc)
            if speaker.replace("\n", "").lower() == "he" and "2" in category.replace("\n", ""):
                accuracies_m_speaker_2.append(acc)

        # for k in range(j+1):
        #     accuracies_total.append(len(corr_all)/len(pred_all))

        if len(accuracies_total) == 0:
            accuracies_total.append(0)
        if len(accuracies_1) == 0:
            accuracies_1.append(0)
        if len(accuracies_2) == 0:
            accuracies_2.append(0)
        if len(accuracies_f_speaker) == 0:
            accuracies_f_speaker.append(0)
        if len(accuracies_m_speaker) == 0:
            accuracies_m_speaker.append(0)
        if len(accuracies_f_speaker_1) == 0:
            accuracies_f_speaker_1.append(0)
        if len(accuracies_f_speaker_2) == 0:
            accuracies_f_speaker_2.append(0)
        if len(accuracies_m_speaker_1) == 0:
            accuracies_m_speaker_1.append(0)
        if len(accuracies_m_speaker_2) == 0:
            accuracies_m_speaker_2.append(0)

    return accuracies_total, accuracies_1, accuracies_2, accuracies_f_speaker, accuracies_m_speaker, \
        accuracies_f_speaker_1, accuracies_f_speaker_2, accuracies_m_speaker_1, accuracies_m_speaker_2


def get_avg_accuracies(accuracies_total, accuracies_1, accuracies_2, accuracies_f_speaker, accuracies_m_speaker, \
    accuracies_f_speaker_1, accuracies_f_speaker_2, accuracies_m_speaker_1, accuracies_m_speaker_2):
    if len(accuracies_total) > 0:
        avg_acc_total = round(np.average(np.array(accuracies_total)) * 100, 1)
    else:
        avg_acc_total = 0
    
    if len(accuracies_f_speaker) > 0:
        avg_acc_f_speaker = round(np.average(np.array(accuracies_f_speaker)) * 100, 1)
    else:
        avg_acc_f_speaker = 0
    if len(accuracies_m_speaker) > 0:
        avg_acc_m_speaker = round(np.average(np.array(accuracies_m_speaker)) * 100, 1)
    else:
        avg_acc_m_speaker = 0

    if len(accuracies_1) > 0:
        avg_acc_1 = round(np.average(np.array(accuracies_1)) * 100, 1)
    else:
        avg_acc_1 = 0
    if len(accuracies_2) > 0:
        avg_acc_2 = round(np.average(np.array(accuracies_2)) * 100, 1)
    else:
        avg_acc_2 = 0

    if len(accuracies_f_speaker_1) > 0:
        avg_acc_f_speaker_1 = round(np.average(np.array(accuracies_f_speaker_1)) * 100, 1)
    else:
        avg_acc_f_speaker_1 = 0
    if len(accuracies_f_speaker_2) > 0:
        avg_acc_f_speaker_2 = round(np.average(np.array(accuracies_f_speaker_2)) * 100, 1)
    else:
        avg_acc_f_speaker_2 = 0
    if len(accuracies_m_speaker_1) > 0:
        avg_acc_m_speaker_1 = round(np.average(np.array(accuracies_m_speaker_1)) * 100, 1)
    else:
        avg_acc_m_speaker_1 = 0
    if len(accuracies_m_speaker_2) > 0:
        avg_acc_m_speaker_2 = round(np.average(np.array(accuracies_m_speaker_2)) * 100, 1)
    else:
        avg_acc_m_speaker_2 = 0

    return avg_acc_total, avg_acc_1, avg_acc_2, avg_acc_f_speaker, avg_acc_m_speaker, \
        avg_acc_f_speaker_1, avg_acc_f_speaker_2, avg_acc_m_speaker_1, avg_acc_m_speaker_2

def calc_and_store_results_per_lset(results, raw_path, pred_path):
    for translation in ["zero_shot", "pivot"]:
        for gender_set in ["all", "feminine", "masculine"]:
            for ref in ["correct_ref", "wrong_ref"]:
                lsets = []
                if translation == "zero_shot":
                    # zero-shot
                    for f in os.listdir(f"{pred_path}/{ref}/{gender_set}"):
                        if os.path.isfile(os.path.join(f"{pred_path}/{ref}/{gender_set}", f)):
                            lset = re.search(r"[a-z][a-z]-[a-z][a-z]", os.path.basename(f)).group(0)
                            sl = lset.split("-")[0]
                            tl = lset.split("-")[1]
                            # if sl in ["fr", "it"] and tl in ["fr", "it"]:
                            if True:
                                lsets.append(lset)
                                if f.endswith(".res"):
                                    # BLEU
                                    # print(f"{pred_path}/{ref}/{gender_set}/{f}")
                                    lines_zs = open(f"{pred_path}/{ref}/{gender_set}/{f}").readlines() 
                                    bleu_zs = get_bleu_scores_mustshe(lines_zs)
                                    results["BLEU"][translation][gender_set][ref][lset] = float(bleu_zs)
                                elif f.startswith(lset) and f.endswith(".pt"):
                                    # Accuracy
                                    acc_total_zs, acc_1_zs, acc_2_zs, acc_f_zs, acc_m_zs, acc_f1_zs, acc_f2_zs, acc_m1_zs, acc_m2_zs = get_accuracies_mustshe(raw_path, pred_path, ref, gender_set, f, sl, tl, pl=None)
                                    avg_acc_total_zs, avg_acc_1_zs, avg_acc_2_zs, avg_acc_f_zs, avg_acc_m_zs, avg_acc_f1_zs, avg_acc_f2_zs, avg_acc_m1_zs, avg_acc_m2_zs = get_avg_accuracies(acc_total_zs, acc_1_zs, acc_2_zs, acc_f_zs, acc_m_zs, acc_f1_zs, acc_f2_zs, acc_m1_zs, acc_m2_zs)
                                    results["accuracy"][translation]["total"][gender_set][ref][lset] = avg_acc_total_zs
                                    results["accuracy"][translation]["1"][gender_set][ref][lset] = avg_acc_1_zs
                                    results["accuracy"][translation]["2"][gender_set][ref][lset] = avg_acc_2_zs
                                    results["accuracy"][translation]["female_speaker"][gender_set][ref][lset] = avg_acc_f_zs
                                    results["accuracy"][translation]["male_speaker"][gender_set][ref][lset] = avg_acc_m_zs

                                    results["accuracy"][translation]["female_speaker_1"][gender_set][ref][lset] = avg_acc_f1_zs
                                    results["accuracy"][translation]["female_speaker_2"][gender_set][ref][lset] = avg_acc_f2_zs
                                    results["accuracy"][translation]["male_speaker_1"][gender_set][ref][lset] = avg_acc_m1_zs
                                    results["accuracy"][translation]["male_speaker_2"][gender_set][ref][lset] = avg_acc_m2_zs
                                else:
                                    continue
                else:
                    # pivot
                    for f in os.listdir(f"{pred_path}/pivot/{ref}/{gender_set}"):
                        if os.path.isfile(os.path.join(f"{pred_path}/pivot/{ref}/{gender_set}", f)):
                            lset = re.search(r"[a-z][a-z]-[a-z][a-z]-[a-z][a-z]", os.path.basename(f)).group(0)
                            sl = lset.split("-")[0]
                            pl = lset.split("-")[1]
                            tl = lset.split("-")[2]
                            lset = f"{sl}-{tl}"
                            
                            if sl != pl and tl != pl:
                                # if sl in ["fr", "it"] and tl in ["fr", "it"]:
                                if True:
                                    lsets.append(lset)
                                    if f.endswith(".res"):
                                        # BLEU
                                        lines_pv = open(f"{pred_path}/pivot/{ref}/{gender_set}/{sl}-{pl}-{tl}.real.pivotout.t.res").readlines()
                                        bleu_pv = get_bleu_scores_mustshe(lines_pv)
                                        results["BLEU"][translation][gender_set][ref][lset] = float(bleu_pv)
                                    elif f.startswith(f"{sl}-{pl}-{tl}") and f.endswith(".pt"):
                                        # Accuracy
                                        acc_total_pv, acc_1_pv, acc_2_pv, acc_f_pv, acc_m_pv, acc_f1_pv, acc_f2_pv, acc_m1_pv, acc_m2_pv = get_accuracies_mustshe(raw_path, pred_path, ref, gender_set, f, sl, tl, pl)
                                        avg_acc_total_pv, avg_acc_1_pv, avg_acc_2_pv, avg_acc_f_pv, avg_acc_m_pv, avg_acc_f1_pv, avg_acc_f2_pv, avg_acc_m1_pv, avg_acc_m2_pv = get_avg_accuracies(acc_total_pv, acc_1_pv, acc_2_pv, acc_f_pv, acc_m_pv, acc_f1_pv, acc_f2_pv, acc_m1_pv, acc_m2_pv)
                                        results["accuracy"][translation]["total"][gender_set][ref][lset] = avg_acc_total_pv
                                        results["accuracy"][translation]["1"][gender_set][ref][lset] = avg_acc_1_pv
                                        results["accuracy"][translation]["2"][gender_set][ref][lset] = avg_acc_2_pv
                                        results["accuracy"][translation]["female_speaker"][gender_set][ref][lset] = avg_acc_f_pv
                                        results["accuracy"][translation]["male_speaker"][gender_set][ref][lset] = avg_acc_m_pv

                                        results["accuracy"][translation]["female_speaker_1"][gender_set][ref][lset] = avg_acc_f1_pv
                                        results["accuracy"][translation]["female_speaker_2"][gender_set][ref][lset] = avg_acc_f2_pv
                                        results["accuracy"][translation]["male_speaker_1"][gender_set][ref][lset] = avg_acc_m1_pv
                                        results["accuracy"][translation]["male_speaker_2"][gender_set][ref][lset] = avg_acc_m2_pv
                                    else:
                                        continue   
                            else:
                                continue

            lsets = set(lsets)
            # additional metrics (I) per gender set
            for lset in set(lsets):
                if translation == "pivot":
                    if lset not in results["BLEU"][translation][gender_set]["wrong_ref"]:
                        continue
                ## I1. BLEU
                results = calc_1__diff_c_w(results, "BLEU", translation, gender_set, lset)
                results = calc_2__sum_c_and_diff_c_w(results, "BLEU", translation, gender_set, lset)

                ## I2. Accuracy (total)
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="total")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="total")
                              
                ## I3. Accuracy (category)
                # -> cat. 1
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="1")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="1")
                # -> cat. 2
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="2")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="2")

                ## I4. Accuracy (speaker)
                # -> female
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="female_speaker")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="female_speaker")
                # -> male
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="male_speaker")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="male_speaker")

                ## I5. Accuracy (cat + speaker)
                # -> cat 1 + female
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="female_speaker_1")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="female_speaker_1")
                # -> cat 2 + female
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="female_speaker_2")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="female_speaker_2")
                # -> cat 1 + male
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="male_speaker_1")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="male_speaker_1")
                # -> cat 2 + male
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="male_speaker_2")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, lset, acc_type="male_speaker_2")

        # additional metrics (II)
        for lset in lsets:
            ## II2. BLEU
            results = calc_3__f_m_of_all_c(results, "BLEU", translation, lset)
            results = calc_4__diff_f_m_of_all_c(results, "BLEU", translation, lset)
            results = calc_5__tradeoff_metric_diff(results, "BLEU", translation, lset)

            ## II2. Accuracy (total)
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, lset, acc_type="total")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, lset, acc_type="total")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, lset, acc_type="total")

            ## II3. Accuracy (category)
            # -> cat. 1
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, lset, acc_type="1")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, lset, acc_type="1")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, lset, acc_type="1")
            # -> cat. 2
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, lset, acc_type="2")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, lset, acc_type="2")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, lset, acc_type="2")

            ## II4. Accuracy (speaker)
            # -> female
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, lset, acc_type="female_speaker")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, lset, acc_type="female_speaker")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, lset, acc_type="female_speaker")
            # -> male
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, lset, acc_type="male_speaker")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, lset, acc_type="male_speaker")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, lset, acc_type="male_speaker")

            ## II5. Accuracy (cat + speaker)
            # -> cat 1 + female
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, lset, acc_type="female_speaker_1")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, lset, acc_type="female_speaker_1")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, lset, acc_type="female_speaker_1")
            # -> cat 2 + female
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, lset, acc_type="female_speaker_2")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, lset, acc_type="female_speaker_2")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, lset, acc_type="female_speaker_2")
            # -> cat 1 + male
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, lset, acc_type="male_speaker_1")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, lset, acc_type="male_speaker_1")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, lset, acc_type="male_speaker_1")
            # -> cat 2 + male
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, lset, acc_type="male_speaker_2")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, lset, acc_type="male_speaker_2")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, lset, acc_type="male_speaker_2")

    return results

def calc_and_store_results_avg_zeroshot_directions(results, raw_path, pred_path):

    for translation in ["zero_shot", "pivot"]:
        for gender_set in ["all", "feminine", "masculine"]:
            for ref in ["correct_ref", "wrong_ref"]:
                if translation == "zero_shot":
                    # zero-shot
                    for f in os.listdir(f"{pred_path}/{ref}/{gender_set}"):
                        if os.path.isfile(os.path.join(f"{pred_path}/{ref}/{gender_set}", f)):
                            lset = re.search(r"[a-z][a-z]-[a-z][a-z]", os.path.basename(f)).group(0)
                            sl = lset.split("-")[0]
                            tl = lset.split("-")[1]
                            if sl in ["fr", "it"] and tl in ["fr", "it"]:
                                # zero-shot direction
                                if f.endswith(".res"):
                                    # BLEU
                                    lines_zs = open(f"{pred_path}/{ref}/{gender_set}/{f}").readlines() 
                                    bleu_zs = get_bleu_scores_mustshe(lines_zs)
                                    if "zs_avg" not in results["BLEU"][translation][gender_set][ref]:
                                        results["BLEU"][translation][gender_set][ref]["zs_avg"] = []
                                    results["BLEU"][translation][gender_set][ref]["zs_avg"].append(float(bleu_zs))
                                elif f.startswith(lset) and f.endswith(".pt"):
                                    # Accuracy
                                    if "zs_avg" not in results["accuracy"][translation]["total"][gender_set][ref]:
                                        results["accuracy"][translation]["total"][gender_set][ref]["zs_avg"] = []
                                        results["accuracy"][translation]["1"][gender_set][ref]["zs_avg"] = []
                                        results["accuracy"][translation]["2"][gender_set][ref]["zs_avg"] = []
                                        results["accuracy"][translation]["female_speaker"][gender_set][ref]["zs_avg"] = []
                                        results["accuracy"][translation]["male_speaker"][gender_set][ref]["zs_avg"] = []

                                        results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["zs_avg"] = []
                                        results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["zs_avg"] = []
                                        results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["zs_avg"] = []
                                        results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["zs_avg"] = []
                                    acc_total_zs, acc_1_zs, acc_2_zs, acc_f_zs, acc_m_zs, acc_f1_zs, acc_f2_zs, acc_m1_zs, acc_m2_zs = get_accuracies_mustshe(raw_path, pred_path, ref, gender_set, f, sl, tl, pl=None)
                                    results["accuracy"][translation]["total"][gender_set][ref]["zs_avg"].append(acc_total_zs)
                                    results["accuracy"][translation]["1"][gender_set][ref]["zs_avg"].append(acc_1_zs)
                                    results["accuracy"][translation]["2"][gender_set][ref]["zs_avg"].append(acc_2_zs)
                                    results["accuracy"][translation]["female_speaker"][gender_set][ref]["zs_avg"].append(acc_f_zs)
                                    results["accuracy"][translation]["male_speaker"][gender_set][ref]["zs_avg"].append(acc_m_zs)

                                    results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["zs_avg"].append(acc_f1_zs)
                                    results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["zs_avg"].append(acc_f2_zs)
                                    results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["zs_avg"].append(acc_m1_zs)
                                    results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["zs_avg"].append(acc_m2_zs)
                                else:
                                    continue
                            else:
                                # not zero-shot direction
                                continue
                else:
                    # pivot
                    for f in os.listdir(f"{pred_path}/pivot/{ref}/{gender_set}"):
                        if os.path.isfile(os.path.join(f"{pred_path}/pivot/{ref}/{gender_set}", f)):
                            lset = re.search(r"[a-z][a-z]-[a-z][a-z]-[a-z][a-z]", os.path.basename(f)).group(0)
                            sl = lset.split("-")[0]
                            pl = lset.split("-")[1]
                            tl = lset.split("-")[2]
                            lset = f"{sl}-{tl}"
                            if sl != pl and tl != pl:
                                if sl in ["fr", "it"] and tl in ["fr", "it"]:
                                    # zero-shot direction
                                    if f.endswith(".res"):
                                        # BLEU
                                        lines_pv = open(f"{pred_path}/pivot/{ref}/{gender_set}/{sl}-{pl}-{tl}.real.pivotout.t.res").readlines()
                                        bleu_pv = get_bleu_scores_mustshe(lines_pv)
                                        if "zs_avg" not in results["BLEU"][translation][gender_set][ref]:
                                            results["BLEU"][translation][gender_set][ref]["zs_avg"] = []
                                        results["BLEU"][translation][gender_set][ref]["zs_avg"].append(float(bleu_pv))
                                    elif f.startswith(f"{sl}-{pl}-{tl}") and f.endswith(".pt"):
                                        # Accuracy
                                        if "zs_avg" not in results["accuracy"][translation]["total"][gender_set][ref]:
                                            results["accuracy"][translation]["total"][gender_set][ref]["zs_avg"] = []
                                            results["accuracy"][translation]["1"][gender_set][ref]["zs_avg"] = []
                                            results["accuracy"][translation]["2"][gender_set][ref]["zs_avg"] = []
                                            results["accuracy"][translation]["female_speaker"][gender_set][ref]["zs_avg"] = []
                                            results["accuracy"][translation]["male_speaker"][gender_set][ref]["zs_avg"] = []

                                            results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["zs_avg"] = []
                                            results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["zs_avg"] = []
                                            results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["zs_avg"] = []
                                            results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["zs_avg"] = []
                                        acc_total_pv, acc_1_pv, acc_2_pv, acc_f_pv, acc_m_pv, acc_f1_pv, acc_f2_pv, acc_m1_pv, acc_m2_pv = get_accuracies_mustshe(raw_path, pred_path, ref, gender_set, f, sl, tl, pl)
                                        results["accuracy"][translation]["total"][gender_set][ref]["zs_avg"].append(acc_total_pv)
                                        results["accuracy"][translation]["1"][gender_set][ref]["zs_avg"].append(acc_1_pv)
                                        results["accuracy"][translation]["2"][gender_set][ref]["zs_avg"].append(acc_2_pv)
                                        results["accuracy"][translation]["female_speaker"][gender_set][ref]["zs_avg"].append(acc_f_pv)
                                        results["accuracy"][translation]["male_speaker"][gender_set][ref]["zs_avg"].append(acc_m_pv)

                                        results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["zs_avg"].append(acc_f1_pv)
                                        results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["zs_avg"].append(acc_f2_pv)
                                        results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["zs_avg"].append(acc_m1_pv)
                                        results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["zs_avg"].append(acc_m2_pv)
                                    else:
                                        continue   
                                else:
                                    # not zero-shot direction
                                    continue
                            else:
                                continue

    for translation in ["zero_shot", "pivot"]:
        for gender_set in ["all", "feminine", "masculine"]:
            for ref in ["correct_ref", "wrong_ref"]:
                bleu_avg = np.round(np.average(results["BLEU"][translation][gender_set][ref]["zs_avg"]), 1)
                acc_total_avg = np.round(np.average(results["accuracy"][translation]["total"][gender_set][ref]["zs_avg"]) * 100, 1)
                acc_1_avg = np.round(np.average(results["accuracy"][translation]["1"][gender_set][ref]["zs_avg"]) * 100, 1)
                acc_2_avg = np.round(np.average(results["accuracy"][translation]["2"][gender_set][ref]["zs_avg"]) * 100, 1)
                acc_fspeaker_avg = np.round(np.average(results["accuracy"][translation]["female_speaker"][gender_set][ref]["zs_avg"]) * 100, 1)
                acc_mspeaker_avg = np.round(np.average(results["accuracy"][translation]["male_speaker"][gender_set][ref]["zs_avg"]) * 100, 1)

                acc_fspeaker_1_avg = np.round(np.average(results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["zs_avg"]) * 100, 1)
                acc_fspeaker_2_avg = np.round(np.average(results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["zs_avg"]) * 100, 1)
                acc_mspeaker_1_avg = np.round(np.average(results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["zs_avg"]) * 100, 1)
                acc_mspeaker_2_avg = np.round(np.average(results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["zs_avg"]) * 100, 1)

                results["BLEU"][translation][gender_set][ref]["zs_avg"] = bleu_avg
                results["accuracy"][translation]["total"][gender_set][ref]["zs_avg"] = acc_total_avg
                results["accuracy"][translation]["1"][gender_set][ref]["zs_avg"] = acc_1_avg
                results["accuracy"][translation]["2"][gender_set][ref]["zs_avg"] = acc_2_avg
                results["accuracy"][translation]["female_speaker"][gender_set][ref]["zs_avg"] = acc_fspeaker_avg
                results["accuracy"][translation]["male_speaker"][gender_set][ref]["zs_avg"] = acc_mspeaker_avg

                results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["zs_avg"] = acc_fspeaker_1_avg
                results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["zs_avg"] = acc_fspeaker_2_avg
                results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["zs_avg"] = acc_mspeaker_1_avg
                results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["zs_avg"] = acc_mspeaker_2_avg

            # additional metrics (I)
            ## I1. BLEU
            results = calc_1__diff_c_w(results, "BLEU", translation, gender_set, "zs_avg")
            results = calc_2__sum_c_and_diff_c_w(results, "BLEU", translation, gender_set, "zs_avg")

            ## I2. Accuracy (total)
            results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="total")
            results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="total")
                        
            ## I3. Accuracy (category)
            # -> cat. 1
            results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="1")
            results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="1")
            # -> cat. 2
            results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="2")
            results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="2")

            ## I4. Accuracy (speaker)
            # -> female
            results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="female_speaker")
            results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="female_speaker")
            # -> male
            results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="male_speaker")
            results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="male_speaker")

            ## I5. Accuracy (cat + speaker)
            # -> cat 1 + female
            results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="female_speaker_1")
            results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="female_speaker_1")
            # -> cat 2 + female
            results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="female_speaker_2")
            results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="female_speaker_2")
            # -> cat 1 + male
            results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="male_speaker_1")
            results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="male_speaker_1")
            # -> cat 2 + male
            results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="male_speaker_2")
            results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "zs_avg", acc_type="male_speaker_2")


        # additional metrics (II)
        ## II2. BLEU
        results = calc_3__f_m_of_all_c(results, "BLEU", translation, "zs_avg")
        results = calc_4__diff_f_m_of_all_c(results, "BLEU", translation, "zs_avg")
        results = calc_5__tradeoff_metric_diff(results, "BLEU", translation, "zs_avg")

        ## II2. Accuracy (total)
        results = calc_3__f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="total")
        results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="total")
        results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "zs_avg", acc_type="total")

        ## II3. Accuracy (category)
        # -> cat. 1
        results = calc_3__f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="1")
        results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="1")
        results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "zs_avg", acc_type="1")
        # -> cat. 2
        results = calc_3__f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="2")
        results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="2")
        results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "zs_avg", acc_type="2")

        ## II4. Accuracy (speaker)
        # -> female
        results = calc_3__f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="female_speaker")
        results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="female_speaker")
        results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "zs_avg", acc_type="female_speaker")
        # -> male
        results = calc_3__f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="male_speaker")
        results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="male_speaker")
        results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "zs_avg", acc_type="male_speaker")

        ## II5. Accuracy (cat + speaker)
        # -> cat 1 + female
        results = calc_3__f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="female_speaker_1")
        results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="female_speaker_1")
        results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "zs_avg", acc_type="female_speaker_1")
        # -> cat 2 + female
        results = calc_3__f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="female_speaker_2")
        results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="female_speaker_2")
        results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "zs_avg", acc_type="female_speaker_2")
        # -> cat 1 + male
        results = calc_3__f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="male_speaker_1")
        results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="male_speaker_1")
        results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "zs_avg", acc_type="male_speaker_1")
        # -> cat 2 + male
        results = calc_3__f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="male_speaker_2")
        results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "zs_avg", acc_type="male_speaker_2")
        results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "zs_avg", acc_type="male_speaker_2")

    return results

def calc_and_store_results_avg_supervised_directions(results, raw_path, pred_path, train_set):

    train_lang = []
    if "EN" in train_set or train_set == "twoway.r32.q" or train_set == "twoway.r32.q.new":
        train_lang.append("en")
    elif "ES" in train_set:
        train_lang.append("es")
    elif "DE" in train_set:
        train_lang.append("de")
    elif "FR" in train_set:
        train_lang.append("fr")
    elif "IT" in train_set:
        train_lang.append("it")

    for translation in ["zero_shot", "pivot"]:
        for gender_set in ["all", "feminine", "masculine"]:
            for ref in ["correct_ref", "wrong_ref"]:
                if translation == "zero_shot":
                    # zero-shot
                    for f in os.listdir(f"{pred_path}/{ref}/{gender_set}"):
                        if os.path.isfile(os.path.join(f"{pred_path}/{ref}/{gender_set}", f)):
                            lset = re.search(r"[a-z][a-z]-[a-z][a-z]", os.path.basename(f)).group(0)
                            sl = lset.split("-")[0]
                            tl = lset.split("-")[1]
                            
                            if sl in train_lang or tl in train_lang:
                                # zero-shot direction
                                if f.endswith(".res"):
                                    # BLEU
                                    lines_zs = open(f"{pred_path}/{ref}/{gender_set}/{f}").readlines() 
                                    bleu_zs = get_bleu_scores_mustshe(lines_zs)
                                    if "sv_avg" not in results["BLEU"][translation][gender_set][ref]:
                                        results["BLEU"][translation][gender_set][ref]["sv_avg"] = []
                                    results["BLEU"][translation][gender_set][ref]["sv_avg"].append(float(bleu_zs))
                                elif f.startswith(lset) and f.endswith(".pt"):
                                    # Accuracy
                                    if "sv_avg" not in results["accuracy"][translation]["total"][gender_set][ref]:
                                        results["accuracy"][translation]["total"][gender_set][ref]["sv_avg"] = []
                                        results["accuracy"][translation]["1"][gender_set][ref]["sv_avg"] = []
                                        results["accuracy"][translation]["2"][gender_set][ref]["sv_avg"] = []
                                        results["accuracy"][translation]["female_speaker"][gender_set][ref]["sv_avg"] = []
                                        results["accuracy"][translation]["male_speaker"][gender_set][ref]["sv_avg"] = []

                                        results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["sv_avg"] = []
                                        results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["sv_avg"] = []
                                        results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["sv_avg"] = []
                                        results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["sv_avg"] = []
                                    acc_total_zs, acc_1_zs, acc_2_zs, acc_f_zs, acc_m_zs, acc_f1_zs, acc_f2_zs, acc_m1_zs, acc_m2_zs = get_accuracies_mustshe(raw_path, pred_path, ref, gender_set, f, sl, tl, pl=None)
                                    results["accuracy"][translation]["total"][gender_set][ref]["sv_avg"].append(acc_total_zs)
                                    results["accuracy"][translation]["1"][gender_set][ref]["sv_avg"].append(acc_1_zs)
                                    results["accuracy"][translation]["2"][gender_set][ref]["sv_avg"].append(acc_2_zs)
                                    results["accuracy"][translation]["female_speaker"][gender_set][ref]["sv_avg"].append(acc_f_zs)
                                    results["accuracy"][translation]["male_speaker"][gender_set][ref]["sv_avg"].append(acc_m_zs)

                                    results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["sv_avg"].append(acc_f1_zs)
                                    results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["sv_avg"].append(acc_f2_zs)
                                    results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["sv_avg"].append(acc_m1_zs)
                                    results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["sv_avg"].append(acc_m2_zs)
                                else:
                                    continue
                            else:
                                # not zero-shot direction
                                continue
                else:
                    # pivot
                    for f in os.listdir(f"{pred_path}/pivot/{ref}/{gender_set}"):
                        if os.path.isfile(os.path.join(f"{pred_path}/pivot/{ref}/{gender_set}", f)):
                            lset = re.search(r"[a-z][a-z]-[a-z][a-z]-[a-z][a-z]", os.path.basename(f)).group(0)
                            sl = lset.split("-")[0]
                            pl = lset.split("-")[1]
                            tl = lset.split("-")[2]
                            lset = f"{sl}-{tl}"
                            if sl != pl and tl != pl:
                                if sl in train_lang or tl in train_lang:
                                    # zero-shot direction
                                    if f.endswith(".res"):
                                        # BLEU
                                        lines_pv = open(f"{pred_path}/pivot/{ref}/{gender_set}/{sl}-{pl}-{tl}.real.pivotout.t.res").readlines()
                                        bleu_pv = get_bleu_scores_mustshe(lines_pv)
                                        if "sv_avg" not in results["BLEU"][translation][gender_set][ref]:
                                            results["BLEU"][translation][gender_set][ref]["sv_avg"] = []
                                        results["BLEU"][translation][gender_set][ref]["sv_avg"].append(float(bleu_pv))
                                    elif f.startswith(f"{sl}-{pl}-{tl}") and f.endswith(".pt"):
                                    # Accuracy
                                        if "sv_avg" not in results["accuracy"][translation]["total"][gender_set][ref]:
                                            results["accuracy"][translation]["total"][gender_set][ref]["sv_avg"] = []
                                            results["accuracy"][translation]["1"][gender_set][ref]["sv_avg"] = []
                                            results["accuracy"][translation]["2"][gender_set][ref]["sv_avg"] = []
                                            results["accuracy"][translation]["female_speaker"][gender_set][ref]["sv_avg"] = []
                                            results["accuracy"][translation]["male_speaker"][gender_set][ref]["sv_avg"] = []

                                            results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["sv_avg"] = []
                                            results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["sv_avg"] = []
                                            results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["sv_avg"] = []
                                            results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["sv_avg"] = []
                                        acc_total_pv, acc_1_pv, acc_2_pv, acc_f_pv, acc_m_pv, acc_f1_pv, acc_f2_pv, acc_m1_pv, acc_m2_pv = get_accuracies_mustshe(raw_path, pred_path, ref, gender_set, f, sl, tl, pl)
                                        results["accuracy"][translation]["total"][gender_set][ref]["sv_avg"].append(acc_total_pv)
                                        results["accuracy"][translation]["1"][gender_set][ref]["sv_avg"].append(acc_1_pv)
                                        results["accuracy"][translation]["2"][gender_set][ref]["sv_avg"].append(acc_2_pv)
                                        results["accuracy"][translation]["female_speaker"][gender_set][ref]["sv_avg"].append(acc_f_pv)
                                        results["accuracy"][translation]["male_speaker"][gender_set][ref]["sv_avg"].append(acc_m_pv)
                                        
                                        results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["sv_avg"].append(acc_f1_pv)
                                        results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["sv_avg"].append(acc_f2_pv)
                                        results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["sv_avg"].append(acc_m1_pv)
                                        results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["sv_avg"].append(acc_m2_pv)
                                    else:
                                        continue   
                                else:
                                    # not zero-shot direction
                                    continue
                            else:
                                continue

    for translation in ["zero_shot", "pivot"]:
        for gender_set in ["all", "feminine", "masculine"]:
            for ref in ["correct_ref", "wrong_ref"]:
                if "sv_avg" in results["BLEU"][translation][gender_set][ref]:
                    bleu_avg = np.round(np.average(results["BLEU"][translation][gender_set][ref]["sv_avg"]), 1)
                    results["BLEU"][translation][gender_set][ref]["sv_avg"] = bleu_avg
                if "sv_avg" in results["accuracy"][translation]["total"][gender_set][ref]:
                    acc_total_avg = np.round(np.average(results["accuracy"][translation]["total"][gender_set][ref]["sv_avg"]) * 100, 1)
                    acc_1_avg = np.round(np.average(results["accuracy"][translation]["1"][gender_set][ref]["sv_avg"]) * 100, 1)
                    acc_2_avg = np.round(np.average(results["accuracy"][translation]["2"][gender_set][ref]["sv_avg"]) * 100, 1)
                    acc_fspeaker_avg = np.round(np.average(results["accuracy"][translation]["female_speaker"][gender_set][ref]["sv_avg"]) * 100, 1)
                    acc_mspeaker_avg = np.round(np.average(results["accuracy"][translation]["male_speaker"][gender_set][ref]["sv_avg"]) * 100, 1)

                    acc_fspeaker_1_avg = np.round(np.average(results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["sv_avg"]) * 100, 1)
                    acc_fspeaker_2_avg = np.round(np.average(results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["sv_avg"]) * 100, 1)
                    acc_mspeaker_1_avg = np.round(np.average(results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["sv_avg"]) * 100, 1)
                    acc_mspeaker_2_avg = np.round(np.average(results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["sv_avg"]) * 100, 1)

                    results["accuracy"][translation]["total"][gender_set][ref]["sv_avg"] = acc_total_avg
                    results["accuracy"][translation]["1"][gender_set][ref]["sv_avg"] = acc_1_avg
                    results["accuracy"][translation]["2"][gender_set][ref]["sv_avg"] = acc_2_avg
                    results["accuracy"][translation]["female_speaker"][gender_set][ref]["sv_avg"] = acc_fspeaker_avg
                    results["accuracy"][translation]["male_speaker"][gender_set][ref]["sv_avg"] = acc_mspeaker_avg

                    results["accuracy"][translation]["female_speaker_1"][gender_set][ref]["sv_avg"] = acc_fspeaker_1_avg
                    results["accuracy"][translation]["female_speaker_2"][gender_set][ref]["sv_avg"] = acc_fspeaker_2_avg
                    results["accuracy"][translation]["male_speaker_1"][gender_set][ref]["sv_avg"] = acc_mspeaker_1_avg
                    results["accuracy"][translation]["male_speaker_2"][gender_set][ref]["sv_avg"] = acc_mspeaker_2_avg

            # additional metrics (I)
            ## I1. BLEU
            if "sv_avg" in results["BLEU"][translation][gender_set]["correct_ref"]:
                results = calc_1__diff_c_w(results, "BLEU", translation, gender_set, "sv_avg")
                results = calc_2__sum_c_and_diff_c_w(results, "BLEU", translation, gender_set, "sv_avg")

            ## I2. Accuracy (total)
            if "sv_avg" in results["accuracy"][translation]["total"][gender_set]["correct_ref"]:
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="total")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="total")
                        
            ## I3. Accuracy (category)
            # -> cat. 1
            if "sv_avg" in results["accuracy"][translation]["1"][gender_set]["correct_ref"]:
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="1")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="1")
            # -> cat. 2
            if "sv_avg" in results["accuracy"][translation]["2"][gender_set]["correct_ref"]:
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="2")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="2")

            ## I4. Accuracy (speaker)
            # -> female
            if "sv_avg" in results["accuracy"][translation]["female_speaker"][gender_set]["correct_ref"]:
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="female_speaker")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="female_speaker")
            # -> male
            if "sv_avg" in results["accuracy"][translation]["male_speaker"][gender_set]["correct_ref"]:
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="male_speaker")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="male_speaker")

            ## I5. Accuracy (cat + speaker)
            # -> cat 1 + female 
            if "sv_avg" in results["accuracy"][translation]["female_speaker"][gender_set]["correct_ref"]:
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="female_speaker_1")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="female_speaker_1")
            # -> cat 2 + female 
            if "sv_avg" in results["accuracy"][translation]["female_speaker"][gender_set]["correct_ref"]:
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="female_speaker_2")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="female_speaker_2")
            # -> cat 1 + male
            if "sv_avg" in results["accuracy"][translation]["male_speaker"][gender_set]["correct_ref"]:
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="male_speaker_1")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="male_speaker_1")
            # -> cat 2 + male
            if "sv_avg" in results["accuracy"][translation]["male_speaker"][gender_set]["correct_ref"]:
                results = calc_1__diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="male_speaker_2")
                results = calc_2__sum_c_and_diff_c_w(results, "accuracy", translation, gender_set, "sv_avg", acc_type="male_speaker_2")


        # additional metrics (II)
        ## II2. BLEU
        if "sv_avg" in results["BLEU"][translation]["all"]["correct_ref"]:
            results = calc_3__f_m_of_all_c(results, "BLEU", translation, "sv_avg")
            results = calc_4__diff_f_m_of_all_c(results, "BLEU", translation, "sv_avg")
            results = calc_5__tradeoff_metric_diff(results, "BLEU", translation, "sv_avg")

        ## II2. Accuracy (total)
        if "sv_avg" in results["accuracy"][translation]["total"]["all"]["correct_ref"]:
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="total")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="total")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "sv_avg", acc_type="total")

        ## II3. Accuracy (category)
        # -> cat. 1
        if "sv_avg" in results["accuracy"][translation]["1"]["all"]["correct_ref"]:
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="1")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="1")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "sv_avg", acc_type="1")
        # -> cat. 2
        if "sv_avg" in results["accuracy"][translation]["2"]["all"]["correct_ref"]:
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="2")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="2")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "sv_avg", acc_type="2")

        ## II4. Accuracy (speaker)
        # -> female
        if "sv_avg" in results["accuracy"][translation]["female_speaker"]["all"]["correct_ref"]:
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="female_speaker")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="female_speaker")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "sv_avg", acc_type="female_speaker")
        # -> male
        if "sv_avg" in results["accuracy"][translation]["male_speaker"]["all"]["correct_ref"]:
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="male_speaker")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="male_speaker")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "sv_avg", acc_type="male_speaker")

        ## II4. Accuracy (cat + speaker)
        # -> cat 1 + female
        if "sv_avg" in results["accuracy"][translation]["female_speaker"]["all"]["correct_ref"]:
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="female_speaker_1")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="female_speaker_1")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "sv_avg", acc_type="female_speaker_1")
        # -> cat 2 + female
        if "sv_avg" in results["accuracy"][translation]["female_speaker"]["all"]["correct_ref"]:
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="female_speaker_2")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="female_speaker_2")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "sv_avg", acc_type="female_speaker_2")
        # -> cat 1 + male
        if "sv_avg" in results["accuracy"][translation]["male_speaker"]["all"]["correct_ref"]:
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="male_speaker_1")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="male_speaker_1")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "sv_avg", acc_type="male_speaker_1")
        # -> cat 2 + male
        if "sv_avg" in results["accuracy"][translation]["male_speaker"]["all"]["correct_ref"]:
            results = calc_3__f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="male_speaker_2")
            results = calc_4__diff_f_m_of_all_c(results, "accuracy", translation, "sv_avg", acc_type="male_speaker_2")
            results = calc_5__tradeoff_metric_diff(results, "accuracy", translation, "sv_avg", acc_type="male_speaker_2")

    return results

def calc_1__diff_c_w(results, metric, translation, gender_set, lset, acc_type=None):
    if metric == "accuracy":
        results[metric][translation][acc_type][gender_set]["diff_c_w"][lset] = (np.round(results[metric][translation][acc_type][gender_set]["correct_ref"][lset] - \
            results[metric][translation][acc_type][gender_set]["wrong_ref"][lset], 1)).item()
    else:
        results[metric][translation][gender_set]["diff_c_w"][lset] = (np.round(results[metric][translation][gender_set]["correct_ref"][lset] - \
            results[metric][translation][gender_set]["wrong_ref"][lset], 1)).item()
    return results

def calc_2__sum_c_and_diff_c_w(results, metric, translation, gender_set, lset, acc_type=None):
    if metric == "accuracy":
        results[metric][translation][acc_type][gender_set]["sum_c_and_diff_c_w"][lset] = (np.round(results[metric][translation][acc_type][gender_set]["correct_ref"][lset] + \
            results[metric][translation][acc_type][gender_set]["diff_c_w"][lset], 1)).item()
    else:
        results[metric][translation][gender_set]["sum_c_and_diff_c_w"][lset] = (np.round(results[metric][translation][gender_set]["correct_ref"][lset] + \
            results[metric][translation][gender_set]["diff_c_w"][lset], 1)).item()
    return results

def calc_3__f_m_of_all_c(results, metric, translation, lset, acc_type=None):
    if metric == "accuracy":
        if lset != "sv_avg" or "sv_avg" in results[metric][translation][acc_type]["feminine"]["correct_ref"]:
            f_c = results[metric][translation][acc_type]["feminine"]["correct_ref"][lset]
            m_c = results[metric][translation][acc_type]["masculine"]["correct_ref"][lset]
            if f_c > 0 and m_c > 0: 
                results[metric][translation][acc_type]["f_of_all_c"][lset] = np.round((f_c / (f_c + m_c)) * 100, 1).item()
                results[metric][translation][acc_type]["m_of_all_c"][lset] = np.round((m_c / (f_c + m_c)) * 100, 1).item()
            else:
                results[metric][translation][acc_type]["f_of_all_c"][lset] = 0.0
                results[metric][translation][acc_type]["m_of_all_c"][lset] = 0.0
    else:
        if lset != "sv_avg" or "sv_avg" in results[metric][translation]["feminine"]["correct_ref"]:
            f_c = results[metric][translation]["feminine"]["correct_ref"][lset]
            m_c = results[metric][translation]["masculine"]["correct_ref"][lset]
            results[metric][translation]["f_of_all_c"][lset] = np.round((f_c / (f_c + m_c)) * 100, 1).item()
            results[metric][translation]["m_of_all_c"][lset] = np.round((m_c / (f_c + m_c)) * 100, 1).item()
    return results

def calc_4__diff_f_m_of_all_c(results, metric, translation, lset, acc_type=None):
    if metric == "accuracy":
        if lset != "sv_avg" or "sv_avg" in results[metric][translation][acc_type]["f_of_all_c"]:
            f_of_all_c = results[metric][translation][acc_type]["f_of_all_c"][lset]
            m_of_all_c = results[metric][translation][acc_type]["m_of_all_c"][lset]
            results[metric][translation][acc_type]["diff_f_m_of_all_c"][lset] = np.round(f_of_all_c - m_of_all_c, 1).item()
    else:
        if lset != "sv_avg" or "sv_avg" in results[metric][translation]["f_of_all_c"]:
            f_of_all_c = results[metric][translation]["f_of_all_c"][lset]
            m_of_all_c = results[metric][translation]["m_of_all_c"][lset]
            results[metric][translation]["diff_f_m_of_all_c"][lset] = np.round(f_of_all_c - m_of_all_c, 1).item()
    return results

def calc_5__tradeoff_metric_diff(results, metric, translation, lset, acc_type=None):
    if metric == "accuracy":
        if lset != "sv_avg" or "sv_avg" in results[metric][translation][acc_type]["feminine"]["sum_c_and_diff_c_w"]:
            f_sum_c_and_diff_c_w = results[metric][translation][acc_type]["feminine"]["sum_c_and_diff_c_w"][lset]
            m_sum_c_and_diff_c_w = results[metric][translation][acc_type]["masculine"]["sum_c_and_diff_c_w"][lset]
            results[metric][translation][acc_type]["tquality_w_gender_performance"][lset] = (np.round((f_sum_c_and_diff_c_w + m_sum_c_and_diff_c_w)/2 - \
                abs(f_sum_c_and_diff_c_w - m_sum_c_and_diff_c_w), 1)).item()
    else:
        if lset != "sv_avg" or "sv_avg" in results[metric][translation]["feminine"]["sum_c_and_diff_c_w"]:
            f_sum_c_and_diff_c_w = results[metric][translation]["feminine"]["sum_c_and_diff_c_w"][lset]
            m_sum_c_and_diff_c_w = results[metric][translation]["masculine"]["sum_c_and_diff_c_w"][lset]
            results[metric][translation]["tquality_w_gender_performance"][lset] = (np.round((f_sum_c_and_diff_c_w + m_sum_c_and_diff_c_w)/2 - \
                abs(f_sum_c_and_diff_c_w - m_sum_c_and_diff_c_w), 1)).item()
    return results
    
def export_results(results, metric, df, out_path, map_train_set_model_name, train_set, acc_type=None, avg_sv=False):
    sl = ''
    tl = ''
    cur_model = ""
    if metric == "BLEU" or acc_type == "total":
        num_rows = 12 * len(map_train_set_model_name) + 2
    else:
        num_rows = 2 * 12 * len(map_train_set_model_name) + 2

    i = -1
    for _ , r in df.iterrows():
        i += 1
        if i < num_rows:
            if i < 2:
                # skip header rows
                continue
            else:
                if sl == '' or not pd.isna(df.loc[i, "sl"]):
                    sl = df.loc[i, "sl"]
                if tl == '' or not pd.isna(df.loc[i, "tl"]):
                    tl = r["tl"]
                if cur_model == "" or not pd.isna(df.loc[i, "model"]):
                    cur_model = r["model"]

                if map_train_set_model_name[train_set] == cur_model:
                    if metric == "BLEU":
                        # check if sl-tl pair is in results
                        if f"{sl}-{tl}" in results[metric]["zero_shot"]["all"]["correct_ref"]:
                            # all
                            df.loc[i, "all_cor_zs"] = results[metric]["zero_shot"]["all"]["correct_ref"][f"{sl}-{tl}"]
                            df.loc[i, "all_wro_zs"] = results[metric]["zero_shot"]["all"]["wrong_ref"][f"{sl}-{tl}"]
                            df.loc[i, "all_diff_zs"] = results[metric]["zero_shot"]["all"]["diff_c_w"][f"{sl}-{tl}"]
                            df.loc[i, "all_sum_diff_zs"] = results[metric]["zero_shot"]["all"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                            # feminine
                            df.loc[i, "f_cor_zs"] = results[metric]["zero_shot"]["feminine"]["correct_ref"][f"{sl}-{tl}"]
                            df.loc[i, "f_wro_zs"] = results[metric]["zero_shot"]["feminine"]["wrong_ref"][f"{sl}-{tl}"]
                            df.loc[i, "f_diff_zs"] = results[metric]["zero_shot"]["feminine"]["diff_c_w"][f"{sl}-{tl}"]
                            df.loc[i, "f_sum_diff_zs"] = results[metric]["zero_shot"]["feminine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                            # masculine
                            df.loc[i, "m_cor_zs"] = results[metric]["zero_shot"]["masculine"]["correct_ref"][f"{sl}-{tl}"]
                            df.loc[i, "m_wro_zs"] = results[metric]["zero_shot"]["masculine"]["wrong_ref"][f"{sl}-{tl}"]
                            df.loc[i, "m_diff_zs"] = results[metric]["zero_shot"]["masculine"]["diff_c_w"][f"{sl}-{tl}"]
                            df.loc[i, "m_sum_diff_zs"] = results[metric]["zero_shot"]["masculine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                            # additional metrics
                            df.loc[i, "f_of_cor_zs"] = results[metric]["zero_shot"]["f_of_all_c"][f"{sl}-{tl}"]
                            df.loc[i, "m_of_cor_zs"] = results[metric]["zero_shot"]["m_of_all_c"][f"{sl}-{tl}"]
                            df.loc[i, "diff_f_m_of_cor_zs"] = results[metric]["zero_shot"]["diff_f_m_of_all_c"][f"{sl}-{tl}"]
                            df.loc[i, "gatq_zs"] = results[metric]["zero_shot"]["tquality_w_gender_performance"][f"{sl}-{tl}"]
                        if f"{sl}-{tl}" in results[metric]["pivot"]["all"]["correct_ref"]:
                            # all
                            df.loc[i, "all_cor_pv"] = results[metric]["pivot"]["all"]["correct_ref"][f"{sl}-{tl}"]
                            df.loc[i, "all_wro_pv"] = results[metric]["pivot"]["all"]["wrong_ref"][f"{sl}-{tl}"]
                            df.loc[i, "all_diff_pv"] = results[metric]["pivot"]["all"]["diff_c_w"][f"{sl}-{tl}"]
                            df.loc[i, "all_sum_diff_pv"] = results[metric]["pivot"]["all"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                            # feminine
                            df.loc[i, "f_cor_pv"] = results[metric]["pivot"]["feminine"]["correct_ref"][f"{sl}-{tl}"]
                            df.loc[i, "f_wro_pv"] = results[metric]["pivot"]["feminine"]["wrong_ref"][f"{sl}-{tl}"]
                            df.loc[i, "f_diff_pv"] = results[metric]["pivot"]["feminine"]["diff_c_w"][f"{sl}-{tl}"]
                            df.loc[i, "f_sum_diff_pv"] = results[metric]["pivot"]["feminine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                            # masculine
                            df.loc[i, "m_cor_pv"] = results[metric]["pivot"]["masculine"]["correct_ref"][f"{sl}-{tl}"]
                            df.loc[i, "m_wro_pv"] = results[metric]["pivot"]["masculine"]["wrong_ref"][f"{sl}-{tl}"]
                            df.loc[i, "m_diff_pv"] = results[metric]["pivot"]["masculine"]["diff_c_w"][f"{sl}-{tl}"]
                            df.loc[i, "m_sum_diff_pv"] = results[metric]["pivot"]["masculine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                            # additional metrics
                            df.loc[i, "f_of_cor_pv"] = results[metric]["pivot"]["f_of_all_c"][f"{sl}-{tl}"]
                            df.loc[i, "m_of_cor_pv"] = results[metric]["pivot"]["m_of_all_c"][f"{sl}-{tl}"]
                            df.loc[i, "diff_f_m_of_cor_pv"] = results[metric]["pivot"]["diff_f_m_of_all_c"][f"{sl}-{tl}"]
                            df.loc[i, "gatq_pv"] = results[metric]["pivot"]["tquality_w_gender_performance"][f"{sl}-{tl}"]

                    if metric == "accuracy":
                        if i % 2 != 0 and (acc_type == "1" or "female_speaker" in acc_type):
                            continue
                        else:
                            # check if sl-tl pair is in results
                            if f"{sl}-{tl}" in results[metric]["zero_shot"][acc_type]["all"]["correct_ref"]:
                                # all
                                df.loc[i, "all_cor_zs"] = results[metric]["zero_shot"][acc_type]["all"]["correct_ref"][f"{sl}-{tl}"]
                                df.loc[i, "all_wro_zs"] = results[metric]["zero_shot"][acc_type]["all"]["wrong_ref"][f"{sl}-{tl}"]
                                df.loc[i, "all_diff_zs"] = results[metric]["zero_shot"][acc_type]["all"]["diff_c_w"][f"{sl}-{tl}"]
                                df.loc[i, "all_sum_diff_zs"] = results[metric]["zero_shot"][acc_type]["all"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                # feminine
                                df.loc[i, "f_cor_zs"] = results[metric]["zero_shot"][acc_type]["feminine"]["correct_ref"][f"{sl}-{tl}"]
                                df.loc[i, "f_wro_zs"] = results[metric]["zero_shot"][acc_type]["feminine"]["wrong_ref"][f"{sl}-{tl}"]
                                df.loc[i, "f_diff_zs"] = results[metric]["zero_shot"][acc_type]["feminine"]["diff_c_w"][f"{sl}-{tl}"]
                                df.loc[i, "f_sum_diff_zs"] = results[metric]["zero_shot"][acc_type]["feminine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                # masculine
                                df.loc[i, "m_cor_zs"] = results[metric]["zero_shot"][acc_type]["masculine"]["correct_ref"][f"{sl}-{tl}"]
                                df.loc[i, "m_wro_zs"] = results[metric]["zero_shot"][acc_type]["masculine"]["wrong_ref"][f"{sl}-{tl}"]
                                df.loc[i, "m_diff_zs"] = results[metric]["zero_shot"][acc_type]["masculine"]["diff_c_w"][f"{sl}-{tl}"]
                                df.loc[i, "m_sum_diff_zs"] = results[metric]["zero_shot"][acc_type]["masculine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                # additional metrics
                                df.loc[i, "f_of_cor_zs"] = results[metric]["zero_shot"][acc_type]["f_of_all_c"][f"{sl}-{tl}"]
                                df.loc[i, "m_of_cor_zs"] = results[metric]["zero_shot"][acc_type]["m_of_all_c"][f"{sl}-{tl}"]
                                df.loc[i, "diff_f_m_of_cor_zs"] = results[metric]["zero_shot"][acc_type]["diff_f_m_of_all_c"][f"{sl}-{tl}"]
                                df.loc[i, "gatq_zs"] = results[metric]["zero_shot"][acc_type]["tquality_w_gender_performance"][f"{sl}-{tl}"]
                            if f"{sl}-{tl}" in results[metric]["pivot"][acc_type]["all"]["correct_ref"]:
                                # all
                                df.loc[i, "all_cor_pv"] = results[metric]["pivot"][acc_type]["all"]["correct_ref"][f"{sl}-{tl}"]
                                df.loc[i, "all_wro_pv"] = results[metric]["pivot"][acc_type]["all"]["wrong_ref"][f"{sl}-{tl}"]
                                df.loc[i, "all_diff_pv"] = results[metric]["pivot"][acc_type]["all"]["diff_c_w"][f"{sl}-{tl}"]
                                df.loc[i, "all_sum_diff_pv"] = results[metric]["pivot"][acc_type]["all"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                # feminine
                                df.loc[i, "f_cor_pv"] = results[metric]["pivot"][acc_type]["feminine"]["correct_ref"][f"{sl}-{tl}"]
                                df.loc[i, "f_wro_pv"] = results[metric]["pivot"][acc_type]["feminine"]["wrong_ref"][f"{sl}-{tl}"]
                                df.loc[i, "f_diff_pv"] = results[metric]["pivot"][acc_type]["feminine"]["diff_c_w"][f"{sl}-{tl}"]
                                df.loc[i, "f_sum_diff_pv"] = results[metric]["pivot"][acc_type]["feminine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                # masculine
                                df.loc[i, "m_cor_pv"] = results[metric]["pivot"][acc_type]["masculine"]["correct_ref"][f"{sl}-{tl}"]
                                df.loc[i, "m_wro_pv"] = results[metric]["pivot"][acc_type]["masculine"]["wrong_ref"][f"{sl}-{tl}"]
                                df.loc[i, "m_diff_pv"] = results[metric]["pivot"][acc_type]["masculine"]["diff_c_w"][f"{sl}-{tl}"]
                                df.loc[i, "m_sum_diff_pv"] = results[metric]["pivot"][acc_type]["masculine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                # additional metrics
                                df.loc[i, "f_of_cor_pv"] = results[metric]["pivot"][acc_type]["f_of_all_c"][f"{sl}-{tl}"]
                                df.loc[i, "m_of_cor_pv"] = results[metric]["pivot"][acc_type]["m_of_all_c"][f"{sl}-{tl}"]
                                df.loc[i, "diff_f_m_of_cor_pv"] = results[metric]["pivot"][acc_type]["diff_f_m_of_all_c"][f"{sl}-{tl}"]
                                df.loc[i, "gatq_pv"] = results[metric]["pivot"][acc_type]["tquality_w_gender_performance"][f"{sl}-{tl}"]

                            acc_type_2 = None
                            if acc_type == "1":
                                acc_type_2 = "2"
                            if acc_type == "female_speaker":
                                acc_type_2 = "male_speaker"
                            if acc_type == "female_speaker_1":
                                acc_type_2 = "male_speaker_1"
                            if acc_type == "female_speaker_2":
                                acc_type_2 = "male_speaker_2"

                            if acc_type_2 == None:
                                continue
                            else:
                                if f"{sl}-{tl}" in results[metric]["zero_shot"][acc_type_2]["all"]["correct_ref"]:
                                    # all
                                    df.loc[i+1, "all_cor_zs"] = results[metric]["zero_shot"][acc_type_2]["all"]["correct_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "all_wro_zs"] = results[metric]["zero_shot"][acc_type_2]["all"]["wrong_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "all_diff_zs"] = results[metric]["zero_shot"][acc_type_2]["all"]["diff_c_w"][f"{sl}-{tl}"]
                                    df.loc[i+1, "all_sum_diff_zs"] = results[metric]["zero_shot"][acc_type_2]["all"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                    # feminine
                                    df.loc[i+1, "f_cor_zs"] = results[metric]["zero_shot"][acc_type_2]["feminine"]["correct_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "f_wro_zs"] = results[metric]["zero_shot"][acc_type_2]["feminine"]["wrong_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "f_diff_zs"] = results[metric]["zero_shot"][acc_type_2]["feminine"]["diff_c_w"][f"{sl}-{tl}"]
                                    df.loc[i+1, "f_sum_diff_zs"] = results[metric]["zero_shot"][acc_type_2]["feminine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                    # masculine
                                    df.loc[i+1, "m_cor_zs"] = results[metric]["zero_shot"][acc_type_2]["masculine"]["correct_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "m_wro_zs"] = results[metric]["zero_shot"][acc_type_2]["masculine"]["wrong_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "m_diff_zs"] = results[metric]["zero_shot"][acc_type_2]["masculine"]["diff_c_w"][f"{sl}-{tl}"]
                                    df.loc[i+1, "m_sum_diff_zs"] = results[metric]["zero_shot"][acc_type_2]["masculine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                    # additional metrics
                                    df.loc[i+1, "f_of_cor_zs"] = results[metric]["zero_shot"][acc_type_2]["f_of_all_c"][f"{sl}-{tl}"]
                                    df.loc[i+1, "m_of_cor_zs"] = results[metric]["zero_shot"][acc_type_2]["m_of_all_c"][f"{sl}-{tl}"]
                                    df.loc[i+1, "diff_f_m_of_cor_zs"] = results[metric]["zero_shot"][acc_type_2]["diff_f_m_of_all_c"][f"{sl}-{tl}"]
                                    df.loc[i+1, "gatq_zs"] = results[metric]["zero_shot"][acc_type_2]["tquality_w_gender_performance"][f"{sl}-{tl}"]
                                if f"{sl}-{tl}" in results[metric]["pivot"][acc_type_2]["all"]["correct_ref"]:
                                    # all
                                    df.loc[i+1, "all_cor_pv"] = results[metric]["pivot"][acc_type_2]["all"]["correct_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "all_wro_pv"] = results[metric]["pivot"][acc_type_2]["all"]["wrong_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "all_diff_pv"] = results[metric]["pivot"][acc_type_2]["all"]["diff_c_w"][f"{sl}-{tl}"]
                                    df.loc[i+1, "all_sum_diff_pv"] = results[metric]["pivot"][acc_type_2]["all"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                    # feminine
                                    df.loc[i+1, "f_cor_pv"] = results[metric]["pivot"][acc_type_2]["feminine"]["correct_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "f_wro_pv"] = results[metric]["pivot"][acc_type_2]["feminine"]["wrong_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "f_diff_pv"] = results[metric]["pivot"][acc_type_2]["feminine"]["diff_c_w"][f"{sl}-{tl}"]
                                    df.loc[i+1, "f_sum_diff_pv"] = results[metric]["pivot"][acc_type_2]["feminine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                    # masculine
                                    df.loc[i+1, "m_cor_pv"] = results[metric]["pivot"][acc_type_2]["masculine"]["correct_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "m_wro_pv"] = results[metric]["pivot"][acc_type_2]["masculine"]["wrong_ref"][f"{sl}-{tl}"]
                                    df.loc[i+1, "m_diff_pv"] = results[metric]["pivot"][acc_type_2]["masculine"]["diff_c_w"][f"{sl}-{tl}"]
                                    df.loc[i+1, "m_sum_diff_pv"] = results[metric]["pivot"][acc_type_2]["masculine"]["sum_c_and_diff_c_w"][f"{sl}-{tl}"]
                                    # additional metrics
                                    df.loc[i+1, "f_of_cor_pv"] = results[metric]["pivot"][acc_type_2]["f_of_all_c"][f"{sl}-{tl}"]
                                    df.loc[i+1, "m_of_cor_pv"] = results[metric]["pivot"][acc_type_2]["m_of_all_c"][f"{sl}-{tl}"]
                                    df.loc[i+1, "diff_f_m_of_cor_pv"] = results[metric]["pivot"][acc_type_2]["diff_f_m_of_all_c"][f"{sl}-{tl}"]
                                    df.loc[i+1, "gatq_pv"] = results[metric]["pivot"][acc_type_2]["tquality_w_gender_performance"][f"{sl}-{tl}"]

    # # average zero-shot directions
    # j = 12 * len(map_train_set_model_name)
    # k = num_rows + 1 + list(map_train_set_model_name.keys()).index(train_set)

    if metric == "BLEU":
        # average zero-shot directions
        d_zs = {
            "sl": "avg. zs",
            "model": map_train_set_model_name[train_set],
            "all_cor_zs": [results[metric]["zero_shot"]["all"]["correct_ref"]["zs_avg"]],
            "all_wro_zs": [results[metric]["zero_shot"]["all"]["wrong_ref"]["zs_avg"]],
            "all_diff_zs": [results[metric]["zero_shot"]["all"]["diff_c_w"]["zs_avg"]],
            "all_sum_diff_zs": [results[metric]["zero_shot"]["all"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "f_cor_zs": [results[metric]["zero_shot"]["feminine"]["correct_ref"]["zs_avg"]],
            "f_wro_zs": [results[metric]["zero_shot"]["feminine"]["wrong_ref"]["zs_avg"]],
            "f_diff_zs": [results[metric]["zero_shot"]["feminine"]["diff_c_w"]["zs_avg"]],
            "f_sum_diff_zs": [results[metric]["zero_shot"]["feminine"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "m_cor_zs": [results[metric]["zero_shot"]["masculine"]["correct_ref"]["zs_avg"]],
            "m_wro_zs": [results[metric]["zero_shot"]["masculine"]["wrong_ref"]["zs_avg"]],
            "m_diff_zs": [results[metric]["zero_shot"]["masculine"]["diff_c_w"]["zs_avg"]],
            "m_sum_diff_zs": [results[metric]["zero_shot"]["masculine"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "f_of_cor_zs": [results[metric]["zero_shot"]["f_of_all_c"]["zs_avg"]],
            "m_of_cor_zs": [results[metric]["zero_shot"]["m_of_all_c"]["zs_avg"]],
            "diff_f_m_of_cor_zs": [results[metric]["zero_shot"]["diff_f_m_of_all_c"]["zs_avg"]],
            "gatq_zs": [results[metric]["zero_shot"]["tquality_w_gender_performance"]["zs_avg"]],


            "all_cor_pv": [results[metric]["pivot"]["all"]["correct_ref"]["zs_avg"]],
            "all_wro_pv": [results[metric]["pivot"]["all"]["wrong_ref"]["zs_avg"]],
            "all_diff_pv": [results[metric]["pivot"]["all"]["diff_c_w"]["zs_avg"]],
            "all_sum_diff_pv": [results[metric]["pivot"]["all"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "f_cor_pv": [results[metric]["pivot"]["feminine"]["correct_ref"]["zs_avg"]],
            "f_wro_pv": [results[metric]["pivot"]["feminine"]["wrong_ref"]["zs_avg"]],
            "f_diff_pv": [results[metric]["pivot"]["feminine"]["diff_c_w"]["zs_avg"]],
            "f_sum_diff_pv": [results[metric]["pivot"]["feminine"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "m_cor_pv": [results[metric]["pivot"]["masculine"]["correct_ref"]["zs_avg"]],
            "m_wro_pv": [results[metric]["pivot"]["masculine"]["wrong_ref"]["zs_avg"]],
            "m_diff_pv": [results[metric]["pivot"]["masculine"]["diff_c_w"]["zs_avg"]],
            "m_sum_diff_pv": [results[metric]["pivot"]["masculine"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "f_of_cor_pv": [results[metric]["pivot"]["f_of_all_c"]["zs_avg"]],
            "m_of_cor_pv": [results[metric]["pivot"]["m_of_all_c"]["zs_avg"]],
            "diff_f_m_of_cor_pv": [results[metric]["pivot"]["diff_f_m_of_all_c"]["zs_avg"]],
            "gatq_pv": [results[metric]["pivot"]["tquality_w_gender_performance"]["zs_avg"]],
        }
        df = pd.concat([df, pd.DataFrame.from_dict(d_zs)])

        # # average supervised directions
        # if avg_sv and "sv_avg" in results[metric]["zero_shot"]["all"]["correct_ref"]:
        #     d_sv = {
        #         "sl": "avg. supervised",
        #         "model": map_train_set_model_name[train_set],
        #         "all_cor_zs": [results[metric]["zero_shot"]["all"]["correct_ref"]["sv_avg"]],
        #         "all_wro_zs": [results[metric]["zero_shot"]["all"]["wrong_ref"]["sv_avg"]],
        #         "all_diff_zs": [results[metric]["zero_shot"]["all"]["diff_c_w"]["sv_avg"]],
        #         "all_sum_diff_zs": [results[metric]["zero_shot"]["all"]["sum_c_and_diff_c_w"]["sv_avg"]],

        #         "f_cor_zs": [results[metric]["zero_shot"]["feminine"]["correct_ref"]["sv_avg"]],
        #         "f_wro_zs": [results[metric]["zero_shot"]["feminine"]["wrong_ref"]["sv_avg"]],
        #         "f_diff_zs": [results[metric]["zero_shot"]["feminine"]["diff_c_w"]["sv_avg"]],
        #         "f_sum_diff_zs": [results[metric]["zero_shot"]["feminine"]["sum_c_and_diff_c_w"]["sv_avg"]],

        #         "m_cor_zs": [results[metric]["zero_shot"]["masculine"]["correct_ref"]["sv_avg"]],
        #         "m_wro_zs": [results[metric]["zero_shot"]["masculine"]["wrong_ref"]["sv_avg"]],
        #         "m_diff_zs": [results[metric]["zero_shot"]["masculine"]["diff_c_w"]["sv_avg"]],
        #         "m_sum_diff_zs": [results[metric]["zero_shot"]["masculine"]["sum_c_and_diff_c_w"]["sv_avg"]],

        #         "f_of_cor_zs": [results[metric]["zero_shot"]["f_of_all_c"]["sv_avg"]],
        #         "m_of_cor_zs": [results[metric]["zero_shot"]["m_of_all_c"]["sv_avg"]],
        #         "diff_f_m_of_cor_zs": [results[metric]["zero_shot"]["diff_f_m_of_all_c"]["sv_avg"]],
        #         "gatq_zs": [results[metric]["zero_shot"]["tquality_w_gender_performance"]["sv_avg"]]
        #     }
        #     df = pd.concat([df, pd.DataFrame.from_dict(d_sv)])

    if metric == "accuracy":

        if acc_type == "1":
            category = "cat. 1"
        elif "female_speaker" in acc_type:
            category = "female"
        else:
            category = ""
        
        # average zero-shot directions
        d_zs = {
            "sl": "avg. zs",
            "model": map_train_set_model_name[train_set],
            "category": category,
            "all_cor_zs": [results[metric]["zero_shot"][acc_type]["all"]["correct_ref"]["zs_avg"]],
            "all_wro_zs": [results[metric]["zero_shot"][acc_type]["all"]["wrong_ref"]["zs_avg"]],
            "all_diff_zs": [results[metric]["zero_shot"][acc_type]["all"]["diff_c_w"]["zs_avg"]],
            "all_sum_diff_zs": [results[metric]["zero_shot"][acc_type]["all"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "f_cor_zs": [results[metric]["zero_shot"][acc_type]["feminine"]["correct_ref"]["zs_avg"]],
            "f_wro_zs": [results[metric]["zero_shot"][acc_type]["feminine"]["wrong_ref"]["zs_avg"]],
            "f_diff_zs": [results[metric]["zero_shot"][acc_type]["feminine"]["diff_c_w"]["zs_avg"]],
            "f_sum_diff_zs": [results[metric]["zero_shot"][acc_type]["feminine"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "m_cor_zs": [results[metric]["zero_shot"][acc_type]["masculine"]["correct_ref"]["zs_avg"]],
            "m_wro_zs": [results[metric]["zero_shot"][acc_type]["masculine"]["wrong_ref"]["zs_avg"]],
            "m_diff_zs": [results[metric]["zero_shot"][acc_type]["masculine"]["diff_c_w"]["zs_avg"]],
            "m_sum_diff_zs": [results[metric]["zero_shot"][acc_type]["masculine"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "f_of_cor_zs": [results[metric]["zero_shot"][acc_type]["f_of_all_c"]["zs_avg"]],
            "m_of_cor_zs": [results[metric]["zero_shot"][acc_type]["m_of_all_c"]["zs_avg"]],
            "diff_f_m_of_cor_zs": [results[metric]["zero_shot"][acc_type]["diff_f_m_of_all_c"]["zs_avg"]],
            "gatq_zs": [results[metric]["zero_shot"][acc_type]["tquality_w_gender_performance"]["zs_avg"]],


            "all_cor_pv": [results[metric]["pivot"][acc_type]["all"]["correct_ref"]["zs_avg"]],
            "all_wro_pv": [results[metric]["pivot"][acc_type]["all"]["wrong_ref"]["zs_avg"]],
            "all_diff_pv": [results[metric]["pivot"][acc_type]["all"]["diff_c_w"]["zs_avg"]],
            "all_sum_diff_pv": [results[metric]["pivot"][acc_type]["all"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "f_cor_pv": [results[metric]["pivot"][acc_type]["feminine"]["correct_ref"]["zs_avg"]],
            "f_wro_pv": [results[metric]["pivot"][acc_type]["feminine"]["wrong_ref"]["zs_avg"]],
            "f_diff_pv": [results[metric]["pivot"][acc_type]["feminine"]["diff_c_w"]["zs_avg"]],
            "f_sum_diff_pv": [results[metric]["pivot"][acc_type]["feminine"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "m_cor_pv": [results[metric]["pivot"][acc_type]["masculine"]["correct_ref"]["zs_avg"]],
            "m_wro_pv": [results[metric]["pivot"][acc_type]["masculine"]["wrong_ref"]["zs_avg"]],
            "m_diff_pv": [results[metric]["pivot"][acc_type]["masculine"]["diff_c_w"]["zs_avg"]],
            "m_sum_diff_pv": [results[metric]["pivot"][acc_type]["masculine"]["sum_c_and_diff_c_w"]["zs_avg"]],

            "f_of_cor_pv": [results[metric]["pivot"][acc_type]["f_of_all_c"]["zs_avg"]],
            "m_of_cor_pv": [results[metric]["pivot"][acc_type]["m_of_all_c"]["zs_avg"]],
            "diff_f_m_of_cor_pv": [results[metric]["pivot"][acc_type]["diff_f_m_of_all_c"]["zs_avg"]],
            "gatq_pv": [results[metric]["pivot"][acc_type]["tquality_w_gender_performance"]["zs_avg"]],
        }
        df = pd.concat([df, pd.DataFrame.from_dict(d_zs)])

        ## second metric (category or speaker)
        if acc_type == "1" or "female_speaker" in acc_type:
            if acc_type == "1":
                acc_type_2 = "2"
                category = "cat. 2"
            elif acc_type == "female_speaker":
                acc_type_2 = "male_speaker"
                category = "male"
            elif acc_type == "female_speaker_1":
                acc_type_2 = "male_speaker_1"
                category = "male"
            elif acc_type == "female_speaker_2":
                acc_type_2 = "male_speaker_2"
                category = "male"
            else:
                pass

            d2_zs = {
                "sl": "avg. zs",
                "model": map_train_set_model_name[train_set],
                "category": category,
                "all_cor_zs": [results[metric]["zero_shot"][acc_type_2]["all"]["correct_ref"]["zs_avg"]],
                "all_wro_zs": [results[metric]["zero_shot"][acc_type_2]["all"]["wrong_ref"]["zs_avg"]],
                "all_diff_zs": [results[metric]["zero_shot"][acc_type_2]["all"]["diff_c_w"]["zs_avg"]],
                "all_sum_diff_zs": [results[metric]["zero_shot"][acc_type_2]["all"]["sum_c_and_diff_c_w"]["zs_avg"]],

                "f_cor_zs": [results[metric]["zero_shot"][acc_type_2]["feminine"]["correct_ref"]["zs_avg"]],
                "f_wro_zs": [results[metric]["zero_shot"][acc_type_2]["feminine"]["wrong_ref"]["zs_avg"]],
                "f_diff_zs": [results[metric]["zero_shot"][acc_type_2]["feminine"]["diff_c_w"]["zs_avg"]],
                "f_sum_diff_zs": [results[metric]["zero_shot"][acc_type_2]["feminine"]["sum_c_and_diff_c_w"]["zs_avg"]],

                "m_cor_zs": [results[metric]["zero_shot"][acc_type_2]["masculine"]["correct_ref"]["zs_avg"]],
                "m_wro_zs": [results[metric]["zero_shot"][acc_type_2]["masculine"]["wrong_ref"]["zs_avg"]],
                "m_diff_zs": [results[metric]["zero_shot"][acc_type_2]["masculine"]["diff_c_w"]["zs_avg"]],
                "m_sum_diff_zs": [results[metric]["zero_shot"][acc_type_2]["masculine"]["sum_c_and_diff_c_w"]["zs_avg"]],

                "f_of_cor_zs": [results[metric]["zero_shot"][acc_type_2]["f_of_all_c"]["zs_avg"]],
                "m_of_cor_zs": [results[metric]["zero_shot"][acc_type_2]["m_of_all_c"]["zs_avg"]],
                "diff_f_m_of_cor_zs": [results[metric]["zero_shot"][acc_type_2]["diff_f_m_of_all_c"]["zs_avg"]],
                "gatq_zs": [results[metric]["zero_shot"][acc_type_2]["tquality_w_gender_performance"]["zs_avg"]],


                "all_cor_pv": [results[metric]["pivot"][acc_type_2]["all"]["correct_ref"]["zs_avg"]],
                "all_wro_pv": [results[metric]["pivot"][acc_type_2]["all"]["wrong_ref"]["zs_avg"]],
                "all_diff_pv": [results[metric]["pivot"][acc_type_2]["all"]["diff_c_w"]["zs_avg"]],
                "all_sum_diff_pv": [results[metric]["pivot"][acc_type_2]["all"]["sum_c_and_diff_c_w"]["zs_avg"]],

                "f_cor_pv": [results[metric]["pivot"][acc_type_2]["feminine"]["correct_ref"]["zs_avg"]],
                "f_wro_pv": [results[metric]["pivot"][acc_type_2]["feminine"]["wrong_ref"]["zs_avg"]],
                "f_diff_pv": [results[metric]["pivot"][acc_type_2]["feminine"]["diff_c_w"]["zs_avg"]],
                "f_sum_diff_pv": [results[metric]["pivot"][acc_type_2]["feminine"]["sum_c_and_diff_c_w"]["zs_avg"]],

                "m_cor_pv": [results[metric]["pivot"][acc_type_2]["masculine"]["correct_ref"]["zs_avg"]],
                "m_wro_pv": [results[metric]["pivot"][acc_type_2]["masculine"]["wrong_ref"]["zs_avg"]],
                "m_diff_pv": [results[metric]["pivot"][acc_type_2]["masculine"]["diff_c_w"]["zs_avg"]],
                "m_sum_diff_pv": [results[metric]["pivot"][acc_type_2]["masculine"]["sum_c_and_diff_c_w"]["zs_avg"]],

                "f_of_cor_pv": [results[metric]["pivot"][acc_type_2]["f_of_all_c"]["zs_avg"]],
                "m_of_cor_pv": [results[metric]["pivot"][acc_type_2]["m_of_all_c"]["zs_avg"]],
                "diff_f_m_of_cor_pv": [results[metric]["pivot"][acc_type_2]["diff_f_m_of_all_c"]["zs_avg"]],
                "gatq_pv": [results[metric]["pivot"][acc_type_2]["tquality_w_gender_performance"]["zs_avg"]],

            }
            df = pd.concat([df, pd.DataFrame.from_dict(d2_zs)])

        # # average supervised directions
        # if avg_sv and "sv_avg" in results[metric]["zero_shot"][acc_type]["all"]["correct_ref"]:
        #     d_sv = {
        #         "sl": "avg. supervised",
        #         "model": map_train_set_model_name[train_set],
        #         "category": category,
        #         "all_cor_zs": [results[metric]["zero_shot"][acc_type]["all"]["correct_ref"]["sv_avg"]],
        #         "all_wro_zs": [results[metric]["zero_shot"][acc_type]["all"]["wrong_ref"]["sv_avg"]],
        #         "all_diff_zs": [results[metric]["zero_shot"][acc_type]["all"]["diff_c_w"]["sv_avg"]],
        #         "all_sum_diff_zs": [results[metric]["zero_shot"][acc_type]["all"]["sum_c_and_diff_c_w"]["sv_avg"]],

        #         "f_cor_zs": [results[metric]["zero_shot"][acc_type]["feminine"]["correct_ref"]["sv_avg"]],
        #         "f_wro_zs": [results[metric]["zero_shot"][acc_type]["feminine"]["wrong_ref"]["sv_avg"]],
        #         "f_diff_zs": [results[metric]["zero_shot"][acc_type]["feminine"]["diff_c_w"]["sv_avg"]],
        #         "f_sum_diff_zs": [results[metric]["zero_shot"][acc_type]["feminine"]["sum_c_and_diff_c_w"]["sv_avg"]],

        #         "m_cor_zs": [results[metric]["zero_shot"][acc_type]["masculine"]["correct_ref"]["sv_avg"]],
        #         "m_wro_zs": [results[metric]["zero_shot"][acc_type]["masculine"]["wrong_ref"]["sv_avg"]],
        #         "m_diff_zs": [results[metric]["zero_shot"][acc_type]["masculine"]["diff_c_w"]["sv_avg"]],
        #         "m_sum_diff_zs": [results[metric]["zero_shot"][acc_type]["masculine"]["sum_c_and_diff_c_w"]["sv_avg"]],

        #         "f_of_cor_zs": [results[metric]["zero_shot"][acc_type]["f_of_all_c"]["sv_avg"]],
        #         "m_of_cor_zs": [results[metric]["zero_shot"][acc_type]["m_of_all_c"]["sv_avg"]],
        #         "diff_f_m_of_cor_zs": [results[metric]["zero_shot"][acc_type]["diff_f_m_of_all_c"]["sv_avg"]],
        #         "gatq_zs": [results[metric]["zero_shot"][acc_type]["tquality_w_gender_performance"]["sv_avg"]]
        #     }
        #     df = pd.concat([df, pd.DataFrame.from_dict(d_sv)])

        ## second metric (category or speaker)
        if acc_type == "1" or "female_speaker" in acc_type:
            if acc_type == "1":
                acc_type_2 = "2"
                category = "cat. 2"
            elif acc_type == "female_speaker":
                acc_type_2 = "male_speaker"
                category = "male"
            elif acc_type == "female_speaker_1":
                acc_type_2 = "male_speaker_1"
                category = "male"
            elif acc_type == "female_speaker_2":
                acc_type_2 = "male_speaker_2"
                category = "male"
            else:
                pass
            
            if avg_sv and "sv_avg" in results[metric]["zero_shot"][acc_type_2]["all"]["correct_ref"]:
                d2_sv = {
                    "sl": "avg. supervised",
                    "model": map_train_set_model_name[train_set],
                    "category": category,
                    "all_cor_zs": [results[metric]["zero_shot"][acc_type_2]["all"]["correct_ref"]["sv_avg"]],
                    "all_wro_zs": [results[metric]["zero_shot"][acc_type_2]["all"]["wrong_ref"]["sv_avg"]],
                    "all_diff_zs": [results[metric]["zero_shot"][acc_type_2]["all"]["diff_c_w"]["sv_avg"]],
                    "all_sum_diff_zs": [results[metric]["zero_shot"][acc_type_2]["all"]["sum_c_and_diff_c_w"]["sv_avg"]],

                    "f_cor_zs": [results[metric]["zero_shot"][acc_type_2]["feminine"]["correct_ref"]["sv_avg"]],
                    "f_wro_zs": [results[metric]["zero_shot"][acc_type_2]["feminine"]["wrong_ref"]["sv_avg"]],
                    "f_diff_zs": [results[metric]["zero_shot"][acc_type_2]["feminine"]["diff_c_w"]["sv_avg"]],
                    "f_sum_diff_zs": [results[metric]["zero_shot"][acc_type_2]["feminine"]["sum_c_and_diff_c_w"]["sv_avg"]],

                    "m_cor_zs": [results[metric]["zero_shot"][acc_type_2]["masculine"]["correct_ref"]["sv_avg"]],
                    "m_wro_zs": [results[metric]["zero_shot"][acc_type_2]["masculine"]["wrong_ref"]["sv_avg"]],
                    "m_diff_zs": [results[metric]["zero_shot"][acc_type_2]["masculine"]["diff_c_w"]["sv_avg"]],
                    "m_sum_diff_zs": [results[metric]["zero_shot"][acc_type_2]["masculine"]["sum_c_and_diff_c_w"]["sv_avg"]],

                    "f_of_cor_zs": [results[metric]["zero_shot"][acc_type_2]["f_of_all_c"]["sv_avg"]],
                    "m_of_cor_zs": [results[metric]["zero_shot"][acc_type_2]["m_of_all_c"]["sv_avg"]],
                    "diff_f_m_of_cor_zs": [results[metric]["zero_shot"][acc_type_2]["diff_f_m_of_all_c"]["sv_avg"]],
                    "gatq_zs": [results[metric]["zero_shot"][acc_type_2]["tquality_w_gender_performance"]["sv_avg"]],


                    # "all_cor_pv": [results[metric]["pivot"][acc_type_2]["all"]["correct_ref"]["sv_avg"]],
                    # "all_wro_pv": [results[metric]["pivot"][acc_type_2]["all"]["wrong_ref"]["sv_avg"]],
                    # "all_diff_pv": [results[metric]["pivot"][acc_type_2]["all"]["diff_c_w"]["sv_avg"]],
                    # "all_sum_diff_pv": [results[metric]["pivot"][acc_type_2]["all"]["sum_c_and_diff_c_w"]["sv_avg"]],

                    # "f_cor_pv": [results[metric]["pivot"][acc_type_2]["feminine"]["correct_ref"]["sv_avg"]],
                    # "f_wro_pv": [results[metric]["pivot"][acc_type_2]["feminine"]["wrong_ref"]["sv_avg"]],
                    # "f_diff_pv": [results[metric]["pivot"][acc_type_2]["feminine"]["diff_c_w"]["sv_avg"]],
                    # "f_sum_diff_pv": [results[metric]["pivot"][acc_type_2]["feminine"]["sum_c_and_diff_c_w"]["sv_avg"]],

                    # "m_cor_pv": [results[metric]["pivot"][acc_type_2]["masculine"]["correct_ref"]["sv_avg"]],
                    # "m_wro_pv": [results[metric]["pivot"][acc_type_2]["masculine"]["wrong_ref"]["sv_avg"]],
                    # "m_diff_pv": [results[metric]["pivot"][acc_type_2]["masculine"]["diff_c_w"]["sv_avg"]],
                    # "m_sum_diff_pv": [results[metric]["pivot"][acc_type_2]["masculine"]["sum_c_and_diff_c_w"]["sv_avg"]],

                    # "f_of_cor_pv": [results[metric]["pivot"][acc_type_2]["f_of_all_c"]["sv_avg"]],
                    # "m_of_cor_pv": [results[metric]["pivot"][acc_type_2]["m_of_all_c"]["sv_avg"]],
                    # "diff_f_m_of_cor_pv": [results[metric]["pivot"][acc_type_2]["diff_f_m_of_all_c"]["sv_avg"]],
                    # "gatq_pv": [results[metric]["pivot"][acc_type_2]["tquality_w_gender_performance"]["sv_avg"]],

                }
                df = pd.concat([df, pd.DataFrame.from_dict(d2_sv)])

    df.to_csv(out_path, index=False, sep=";")
    return df

def get_accuracies_mustshe(raw_path, pred_path, ref, gender_set, f, sl, tl, pl): #, results):
    i = 1
    l = tl
    if tl == "en":
        l = sl
    
    gterms_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    if ref == "correct_ref":
        op_gterms_file = open(f"{raw_path}/wrong_ref/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    else:
        op_gterms_file = open(f"{raw_path}/correct_ref/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    speaker_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_speaker.csv", "r", encoding="utf-8")
    category_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_category.csv", "r", encoding="utf-8")
    
    # target reference file (correct/wrong)
    tref_file = open(f"{raw_path}/{ref}/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")

    # swapped "opposite" target reference
    if ref == "correct_ref":
        op_tref_file = open(f"{raw_path}/wrong_ref/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")
    else:
        op_tref_file = open(f"{raw_path}/correct_ref/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")

    # pred file
    if pl == None:
        pred_file = open(f"{pred_path}/{ref}/{gender_set}/{f}", "r", encoding="utf-8")
    else:
        pred_file = open(f"{pred_path}/pivot/{ref}/{gender_set}/{sl}-{pl}-{tl}.real.pivotout.t.pt", "r", encoding="utf-8")

    c_accuracies_total = []
    w_accuracies_total = []
    accuracies_1 = []
    accuracies_2 = []
    accuracies_f_speaker = []
    accuracies_m_speaker = []
    accuracies_f_speaker_1 = []
    accuracies_f_speaker_2 = []
    accuracies_m_speaker_1 = []
    accuracies_m_speaker_2 = []

    c_n_pred = []
    w_n_pred = []
    c_n_corr = []
    w_n_corr = []
    c_pred_all = []
    w_pred_all = []
    c_corr_all = []
    w_corr_all = []

    if tl != "en":
        for j, (tref, op_tref, pred, gterms, op_gterms, speaker, category) in enumerate(zip(tref_file, op_tref_file, pred_file, gterms_file, op_gterms_file, speaker_file, category_file)):
            tref_ = tref.strip()
            op_tref_ = op_tref.strip()
            gterms_list = gterms.split()
            op_gterms_list = op_gterms.split()

            # # correct reference
            # if tref_ in [e.strip() for e in corrected_references[l].keys()]:
            #     tref = corrected_references[l][tref_]
            # if op_tref_ in [e.strip() for e in corrected_references[l].keys()]:
            #     op_tref = corrected_references[l][op_tref_]

            # if tref_ in [e.strip() for e in corrected_gterms[l].keys()]:
            #     # correct gender terms
            #     gterms_list = corrected_gterms[l][tref_].split()
            
            punctuation_marks = [".", ",", "!", "?", ":", ";", "¿", "¡", "\"", "\n", "(", ")", "...", "—", "«", "»"]
            for p_mark in punctuation_marks:
                tref = tref.replace(p_mark, " " + p_mark)
                op_tref = op_tref.replace(p_mark, " " + p_mark)
                pred = pred.replace(p_mark, " " + p_mark)
            tref_list = tref.split()
            op_tref_list = op_tref.split()
            pred_list = pred.split()
             
            # apply upperbound to gender terms, to prevent rewarding over-generated terms
            # gterms_list = list(set(gterms_list))
            # op_gterms_list = list(set(op_gterms_list))

            keep_expr = ["un", "une", "una", "l", "qu", "J", "j", "d", "D", "n", "N"]
            tref_list_ = []
            for t in tref_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    tref_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            tref_list_.append(st)
                else:
                    tref_list_.append(t)

            op_tref_list_ = []
            for t in op_tref_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    op_tref_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            op_tref_list_.append(st)
                else:
                    op_tref_list_.append(t)

            pred_list_ = []
            for t in pred_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    pred_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            pred_list_.append(st)
                else:
                    pred_list_.append(t)

            tref_list = tref_list_
            op_tref_list = op_tref_list_
            pred_list = pred_list_

            # g_w_indices = []
            # for i, (tw, otw) in enumerate(zip(tref_list, op_tref_list)):
            #     # check where correct and wrong ref. differ and store word index
            #     if tw != otw:
            #         # if j == IDX:
            #         #     print(tw, i)
            #         g_w_indices.append(i)

            # # check correct gterm with pred. words ~ gterm pos. idx.
            # n_forward, n_backward = 2, 2  # buffer around orig. gterm pos. idx.
            # pred_gterms = []
            # for i, gterm in enumerate(gterms_list):
            #     pred_all.append(gterm)
            #     if len(g_w_indices) > 0 and i < len(g_w_indices):
            #         idx = g_w_indices[i]
            #         # print(pred_list[idx-n_backward:idx+n_forward])
            #         if gterm in pred_list[idx-n_backward:idx+n_forward]:
            #             pred_gterms.append(gterm)
            #             corr_all.append(gterm)
            #     # else:
            #     #     if gterm in pred_list:
            #     #         pred_gterms.append(gterm)

            # Bentivogli et al.
            c_pred_gterms = []
            w_pred_gterms = []
            c_pred_check = pred_list
            w_pred_check = pred_list
            for c_term, w_term in zip(gterms_list, op_gterms_list):
                c_pred_all.append(c_term)
                w_pred_all.append(w_term)
                if c_term in c_pred_check:
                    c_pred_gterms.append(c_term)
                    c_corr_all.append(c_term)
                    for k in range(len(c_pred_check)):
                        if c_pred_check[k] == c_term:
                            del c_pred_check[k]
                            break

                if w_term in w_pred_check:
                    w_pred_gterms.append(w_term)
                    w_corr_all.append(w_term)
                    for k in range(len(w_pred_check)):
                        if w_pred_check[k] == w_term:
                            del w_pred_check[k]
                            break

            # compute accuracy
            c_acc = len(c_pred_gterms) / len(gterms_list)    
            c_n_pred.append(len(gterms_list))
            c_n_corr.append(len(c_pred_gterms)) 
            w_acc = len(w_pred_gterms) / len(op_gterms_list)    
            w_n_pred.append(len(op_gterms_list))
            w_n_corr.append(len(w_pred_gterms)) 

            # if j == IDX:
            #     # if sl == "it" and tl == "fr":
            #     if sl == "fr" and tl == "it":
            #         print("ACC ref, tref, hyp\n", tref, op_tref, pred)
            #         print(gterms_list)
            #         print(c_pred_gterms)
            #         print(c_acc)
            #         print("---")
            #         print(op_gterms_list)
            #         print(w_pred_gterms)
            #         print(w_acc)
            #         print("===")

            c_accuracies_total.append(c_acc)
            w_accuracies_total.append(w_acc)

            if speaker.replace("\n", "").lower() == "she":
                accuracies_f_speaker.append(c_acc)
            if speaker.replace("\n", "").lower() == "he":
                accuracies_m_speaker.append(c_acc)
            # gender of referred entity
            if "1" in category.replace("\n", ""):
                accuracies_1.append(c_acc)
            if "2" in category.replace("\n", ""):
                accuracies_2.append(c_acc)

            if speaker.replace("\n", "").lower() == "she" and "1" in category.replace("\n", ""):
                accuracies_f_speaker_1.append(c_acc)
            if speaker.replace("\n", "").lower() == "she" and "2" in category.replace("\n", ""):
                accuracies_f_speaker_2.append(c_acc)
            if speaker.replace("\n", "").lower() == "he" and "1" in category.replace("\n", ""):
                accuracies_m_speaker_1.append(c_acc)
            if speaker.replace("\n", "").lower() == "he" and "2" in category.replace("\n", ""):
                accuracies_m_speaker_2.append(c_acc)

        # for k in range(j+1):
        #     accuracies_total.append(len(corr_all)/len(pred_all))

        if len(c_accuracies_total) == 0:
            c_accuracies_total.append(0)
        if len(accuracies_1) == 0:
            accuracies_1.append(0)
        if len(accuracies_2) == 0:
            accuracies_2.append(0)
        if len(accuracies_f_speaker) == 0:
            accuracies_f_speaker.append(0)
        if len(accuracies_m_speaker) == 0:
            accuracies_m_speaker.append(0)
        if len(accuracies_f_speaker_1) == 0:
            accuracies_f_speaker_1.append(0)
        if len(accuracies_f_speaker_2) == 0:
            accuracies_f_speaker_2.append(0)
        if len(accuracies_m_speaker_1) == 0:
            accuracies_m_speaker_1.append(0)
        if len(accuracies_m_speaker_2) == 0:
            accuracies_m_speaker_2.append(0)

    return c_accuracies_total, accuracies_1, accuracies_2, accuracies_f_speaker, accuracies_m_speaker, \
        accuracies_f_speaker_1, accuracies_f_speaker_2, accuracies_m_speaker_1, accuracies_m_speaker_2






def get_sentence_bleu_scores_mustshe(c_references, w_references, hypotheses): #, lset, results):
    i = IDX

    # remove punctuation
    punctuation_marks = [".", ",", "!", "?", ":", ";", "¿", "¡", "\"", "\n", "(", ")", "...", "—", "«", "»"]
    hyps, c_refs, w_refs = [], [], []
    c_refs_corp, w_refs_corp = [], []
    for c_r, w_r, h in zip(c_references, w_references, hypotheses):
        h_puncts = punctuation_marks[:]
        while any(p in h for p in h_puncts):
            h = h.replace(h_puncts[0], "")
            h_puncts = h_puncts[1:]
        h_ = h
        if "'" in h:
            h = h.split("'")
            h_ = ""
            for k in range(len(h)):
                if k == len(h)-1:
                    h_ += h[k]
                else:
                    h_ += h[k] + "' "
        hyps.append(h_.split())

        c_puncts = punctuation_marks[:]
        while any(p in c_r for p in c_puncts):
            c_r = c_r.replace(c_puncts[0], "")
            c_puncts = c_puncts[1:]
        c_r_ = c_r
        if "'" in c_r:
            c_r = c_r.split("'")
            c_r_ = ""
            for k in range(len(c_r)):
                if k == len(c_r)-1:
                    c_r_ += c_r[k]
                else:
                    c_r_ += c_r[k] + "' "
        c_refs.append(c_r_.split())
        c_refs_corp.append([c_r_.split()])

        w_puncts = punctuation_marks[:]
        while any(p in w_r for p in w_puncts):
            w_r = w_r.replace(w_puncts[0], "")
            w_puncts = w_puncts[1:]
        w_r_ = w_r
        if "'" in w_r:
            w_r = w_r.split("'")
            w_r_ = ""
            for k in range(len(w_r)):
                if k == len(w_r)-1:
                    w_r_ += w_r[k]
                else:
                    w_r_ += w_r[k] + "' "
        w_refs.append(w_r_.split())
        w_refs_corp.append([w_r_.split()])

    # hyps = [h.split() for h in hypotheses]
    # refs_c = [r.split() for r in c_references]
    # refs_w = [r.split() for r in w_references]
    
    # c_refs_corp = [[r.split()] for r in c_references]
    # w_refs_corp = [[r.split()] for r in w_references]

    cc = ['Am', 'selben', 'Tag', 'ging', 'sie', 'zu', 'ihm', 'nach', 'Hause']
    ww = ['Am', 'selben', 'Tag', 'ging', 'er', 'zu', 'ihr', 'nach', 'Hause']
    hh = ['Am', 'selben', 'Tag', 'ging', 'sie', 'zu', 'ihr', 'nach', 'Hause']
    print(cc)
    print(ww)
    print(hh)
    weights = (0.25, 0.25, 0.25, 0.25)
    print("cc:", nltk.translate.bleu_score.sentence_bleu([cc], hh, smoothing_function=None, weights=weights) * 100)
    print("ww:", nltk.translate.bleu_score.sentence_bleu([ww], hh, smoothing_function=None, weights=weights) * 100)
    print(['Sie', 'ihm'])
    print(['Sie'])
    print(len(['ihm'])/len(['Sie', 'ihm']))
    print(['Er', 'ihr'])
    print(['ihr'])
    print(len(['ihr'])/len(['Er', 'ihr']))
    exit()

    c_bleu_sent = []
    w_bleu_sent = []
    for j, (c_reference, w_reference, hypothesis) in enumerate(zip(c_refs, w_refs, hyps)):
        smoothing_funct = SmoothingFunction().method1

        c_score = nltk.translate.bleu_score.sentence_bleu([c_reference], hypothesis, smoothing_function=smoothing_funct) * 100
        w_score = nltk.translate.bleu_score.sentence_bleu([w_reference], hypothesis, smoothing_function=smoothing_funct) * 100
        
        if j == i:

            crop_c_ref = c_refs[j]
            crop_w_ref = w_refs[j]

            # # FR, idx=24, 'une' idx=38
            # crop_c_ref = c_refs[j][:38] + c_refs[j][39:]
            # crop_w_ref = w_refs[j][:38] + w_refs[j][39:]

            # print(crop_c_ref)
            # print(crop_w_ref)
            # # IT, idx=28, idx=40, gterms indices: 15, 16, 18, 19, 20, 22, 25, 32 (22 -> W>C, 23 -> W=C, 24 -> W<C)
            # crop_c_ref = c_refs[j][:23] #+ c_refs[j][24:39] + c_refs[j][40:43] + c_refs[j][44:] 
            # crop_w_ref = w_refs[j][:23] #+ w_refs[j][24:39] + w_refs[j][40:43] + w_refs[j][44:] 

            # FR-IT, IDX=27, 14_dei, 15_suoi, 17_cari, 18_amici, 19_quests, 21_anziane (24, 38, 41 -> flips BLEU)
            # crop_c_ref = c_refs[j][:23] + c_refs[j][24:37] + c_refs[j][38:41] + c_refs[j][42:]
            # crop_w_ref = w_refs[j][:23] + w_refs[j][24:37] + w_refs[j][38:41] + w_refs[j][42:]

            # FR-IT, IDX=76, 2_una, 3_delle, 4_mie, 6_amiche, 7_una, 8_bellissima, 10_keniano (13 -> flips BLEU)
            # crop_c_ref = c_refs[j][:12] + c_refs[j][13:]
            # crop_w_ref = w_refs[j][:12] + w_refs[j][13:]

            # FR-IT, IDX=23, 2_una, 3_delle, 4_mie, 6_amiche, 7_una, 8_bellissima, 10_keniano (13 -> flips BLEU)
            # crop_c_ref = c_refs[j][:12] + c_refs[j][13:]
            # crop_w_ref = w_refs[j][:12] + w_refs[j][13:]

            # # FR-IT, IDX=96, 9_10_un'idealista
            # crop_c_ref = c_refs[j][:9] + c_refs[j][9:]
            # crop_w_ref = w_refs[j][:9] + w_refs[j][9:]

            # FR-IT, IDX=103, TODO una, una <- twice -> problem if accu. considers upper bound of matched unique words

            # FR-IT, IDX=76, 7_amiche, 11_keniana
            # crop_c_ref = c_refs[j][:13]
            # crop_w_ref = w_refs[j][:13]

            # crop_c_ref = ['Ma', 'poi', 'una', 'bellissima', 'delle', 'donna', 'mie', 'migliori', 'keniana', 'Esther', 'amiche', 'una']
            # crop_w_ref = ['Ma', 'poi', 'uno', 'bellissimo', 'dei', 'donna', 'miei', 'migliori', 'keniano', 'Esther', 'amici', 'un']

            # h = ['Ma', 'poi', 'uno', 'bellissima', 'dei', 'donna', 'miei', 'migliori', 'keniana', 'Esther', 'amici', 'una']
            # samae as above with swapped word order 
            # crop_c_ref = c_refs[j][7:11] + c_refs[j][:7] + c_refs[j][11:13]
            # crop_w_ref = w_refs[j][7:11] + w_refs[j][:7] + w_refs[j][11:13]

            print(crop_c_ref)
            print(crop_w_ref)
            h = hyps[i]#[15:24]
            # # h = h[6:10] + h[:6] + h[10:12]
            # # print(h[4:6])
            # h = h[:12]
            print(h)

            print("c:", c_score)
            print("w:", w_score)
            weights = (0.25, 0.25, 0.25, 0.25)
            # weights = (1, 0, 0, 0)
            # weights = (0.5, 0.5, 0, 0)
            # weights = (1/3, 1/3, 1/3, 0)
            # weights = (1/3, 1/3, 0, 1/3)
            # weights = (0, 0, 1, 0) # IDX = 27
            print("c (crop):", nltk.translate.bleu_score.sentence_bleu([crop_c_ref], h, smoothing_function=smoothing_funct, weights=weights) * 100)
            print("w (crop):", nltk.translate.bleu_score.sentence_bleu([crop_w_ref], h, smoothing_function=smoothing_funct, weights=weights) * 100)
            # continue

        # if j in [27, 103]:
        # if j in [27, 76, 101, 100, 99, 98, 97]:
        #     continue
    
        c_bleu_sent.append(c_score)
        w_bleu_sent.append(w_score)

    c_bleu_corp = nltk.translate.bleu_score.corpus_bleu(c_refs_corp, hyps, smoothing_function=smoothing_funct) * 100
    w_bleu_corp = nltk.translate.bleu_score.corpus_bleu(w_refs_corp, hyps, smoothing_function=smoothing_funct) * 100
    print("C (corp):", c_bleu_corp)
    print("W (corp):", w_bleu_corp)

    return np.array(c_bleu_sent), np.array(w_bleu_sent)

def get_sentence_accuracy_scores_mustshe_debug(raw_path, pred_path, ref, gender_set, f, sl, tl, pl): #, results):
    i = 1
    l = tl
    if tl == "en":
        l = sl
    
    gterms_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    if ref == "correct_ref":
        op_gterms_file = open(f"{raw_path}/wrong_ref/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    else:
        op_gterms_file = open(f"{raw_path}/correct_ref/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")
    speaker_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_speaker.csv", "r", encoding="utf-8")
    category_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_category.csv", "r", encoding="utf-8")
    
    # target reference file (correct/wrong)
    tref_file = open(f"{raw_path}/{ref}/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")

    # swapped "opposite" target reference
    if ref == "correct_ref":
        op_tref_file = open(f"{raw_path}/wrong_ref/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")
    else:
        op_tref_file = open(f"{raw_path}/correct_ref/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")

    # pred file
    if pl == None:
        pred_file = open(f"{pred_path}/{ref}/{gender_set}/{f}", "r", encoding="utf-8")
    else:
        pred_file = open(f"{pred_path}/pivot/{ref}/{gender_set}/{sl}-{pl}-{tl}.real.pivotout.t.pt", "r", encoding="utf-8")

    c_accuracies_total = []
    w_accuracies_total = []
    accuracies_1 = []
    accuracies_2 = []
    accuracies_f_speaker = []
    accuracies_m_speaker = []
    accuracies_f_speaker_1 = []
    accuracies_f_speaker_2 = []
    accuracies_m_speaker_1 = []
    accuracies_m_speaker_2 = []

    c_n_pred = []
    w_n_pred = []
    c_n_corr = []
    w_n_corr = []
    c_pred_all = []
    w_pred_all = []
    c_corr_all = []
    w_corr_all = []

    if tl != "en":
        for j, (tref, op_tref, pred, gterms, op_gterms, speaker, category) in enumerate(zip(tref_file, op_tref_file, pred_file, gterms_file, op_gterms_file, speaker_file, category_file)):
            tref_ = tref.strip()
            op_tref_ = op_tref.strip()
            gterms_list = gterms.split()
            op_gterms_list = op_gterms.split()

            # # correct reference
            # if tref_ in [e.strip() for e in corrected_references[l].keys()]:
            #     tref = corrected_references[l][tref_]
            # if op_tref_ in [e.strip() for e in corrected_references[l].keys()]:
            #     op_tref = corrected_references[l][op_tref_]

            # if tref_ in [e.strip() for e in corrected_gterms[l].keys()]:
            #     # correct gender terms
            #     gterms_list = corrected_gterms[l][tref_].split()
            
            punctuation_marks = [".", ",", "!", "?", ":", ";", "¿", "¡", "\"", "\n", "(", ")", "...", "—", "«", "»"]
            for p_mark in punctuation_marks:
                tref = tref.replace(p_mark, " " + p_mark)
                op_tref = op_tref.replace(p_mark, " " + p_mark)
                pred = pred.replace(p_mark, " " + p_mark)
            tref_list = tref.split()
            op_tref_list = op_tref.split()
            pred_list = pred.split()
             
            # apply upperbound to gender terms, to prevent rewarding over-generated terms
            # gterms_list = list(set(gterms_list))
            # op_gterms_list = list(set(op_gterms_list))

            keep_expr = ["un", "une", "una", "l", "qu", "J", "j", "d", "D", "n", "N"]
            tref_list_ = []
            for t in tref_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    tref_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            tref_list_.append(st)
                else:
                    tref_list_.append(t)

            op_tref_list_ = []
            for t in op_tref_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    op_tref_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            op_tref_list_.append(st)
                else:
                    op_tref_list_.append(t)

            pred_list_ = []
            for t in pred_list:
                split_tok = re.split('\'', t)
                if len(split_tok) > 1:
                    no_keep = True
                    for st in split_tok:
                        if no_keep:
                            for keep in keep_expr:
                                if keep in st:
                                    st += "'"
                                    pred_list_.append(st)
                                    no_keep = False
                                    break
                        else:
                            pred_list_.append(st)
                else:
                    pred_list_.append(t)

            tref_list = tref_list_
            op_tref_list = op_tref_list_
            pred_list = pred_list_

            # g_w_indices = []
            # for i, (tw, otw) in enumerate(zip(tref_list, op_tref_list)):
            #     # check where correct and wrong ref. differ and store word index
            #     if tw != otw:
            #         # if j == IDX:
            #         #     print(tw, i)
            #         g_w_indices.append(i)

            # # check correct gterm with pred. words ~ gterm pos. idx.
            # n_forward, n_backward = 2, 2  # buffer around orig. gterm pos. idx.
            # pred_gterms = []
            # for i, gterm in enumerate(gterms_list):
            #     pred_all.append(gterm)
            #     if len(g_w_indices) > 0 and i < len(g_w_indices):
            #         idx = g_w_indices[i]
            #         # print(pred_list[idx-n_backward:idx+n_forward])
            #         if gterm in pred_list[idx-n_backward:idx+n_forward]:
            #             pred_gterms.append(gterm)
            #             corr_all.append(gterm)
            #     # else:
            #     #     if gterm in pred_list:
            #     #         pred_gterms.append(gterm)

            # Bentivogli et al.
            c_pred_gterms = []
            w_pred_gterms = []
            c_pred_check = pred_list
            w_pred_check = pred_list
            for c_term, w_term in zip(gterms_list, op_gterms_list):
                c_pred_all.append(c_term)
                w_pred_all.append(w_term)
                if c_term in c_pred_check:
                    c_pred_gterms.append(c_term)
                    c_corr_all.append(c_term)
                    for k in range(len(c_pred_check)):
                        if c_pred_check[k] == c_term:
                            del c_pred_check[k]
                            break

                if w_term in w_pred_check:
                    w_pred_gterms.append(w_term)
                    w_corr_all.append(w_term)
                    for k in range(len(w_pred_check)):
                        if w_pred_check[k] == w_term:
                            del w_pred_check[k]
                            break

            # compute accuracy
            c_acc = len(c_pred_gterms) / len(gterms_list)    
            c_n_pred.append(len(gterms_list))
            c_n_corr.append(len(c_pred_gterms)) 
            w_acc = len(w_pred_gterms) / len(op_gterms_list)    
            w_n_pred.append(len(op_gterms_list))
            w_n_corr.append(len(w_pred_gterms)) 

            if j == IDX:
                if sl == "it" and tl == "fr":
                # if sl == "fr" and tl == "it":
                    print("ACC ref, tref, hyp\n", tref, op_tref, pred)
                    print(gterms_list)
                    print(c_pred_gterms)
                    print(c_acc)
                    print("---")
                    print(op_gterms_list)
                    print(w_pred_gterms)
                    print(w_acc)
                    print("===")
                    # continue

            # if j in [27, 103]:
            # if j in [27, 76, 101, 100, 99, 98, 97]:
            #     continue

            c_accuracies_total.append(c_acc)
            w_accuracies_total.append(w_acc)

    return c_accuracies_total, w_accuracies_total

def sent_level_calc_and_store_results_per_lset_debug(results, raw_path, pred_path):
    for translation in ["zero_shot", "pivot"]:
    # for translation in ["zero_shot"]:
        # for gender_set in ["all", "feminine", "masculine"]:
        for ref in ["correct_ref"]: #, "wrong_ref"]:
            for gender_set in ["feminine"]:
                if translation == "zero_shot":
                    # zero-shot
                    for f in os.listdir(f"{pred_path}/{ref}/{gender_set}"):
                        if os.path.isfile(os.path.join(f"{pred_path}/{ref}/{gender_set}", f)):
                            lset = re.search(r"[a-z][a-z]-[a-z][a-z]", os.path.basename(f)).group(0)
                            sl = lset.split("-")[0]
                            tl = lset.split("-")[1]

                            # if sl in ["fr", "it"] and tl in ["fr", "it"]:
                            if sl in ["it"] and tl in ["fr"]:
                            # if sl in ["fr"] and tl in ["it"]:
                                # zero-shot direction
                                if f.endswith(".pred.pt"):
                                    print()
                                    print(translation, lset)
                                    # BLEU
                                    hypotheses = open(f"{pred_path}/{ref}/{gender_set}/{f}").readlines()
                                    c_references = open(f"{raw_path}/correct_ref/{gender_set}/{sl}-{tl}.t").readlines()                                    
                                    w_references = open(f"{raw_path}/wrong_ref/{gender_set}/{sl}-{tl}.t").readlines()                                    
                                    c_bleu_sent, w_bleu_sent = get_sentence_bleu_scores_mustshe(c_references, w_references, hypotheses)
                                    results["BLEU"][translation][gender_set]["correct_ref"][lset] = c_bleu_sent
                                    results["BLEU"][translation][gender_set]["wrong_ref"][lset] = w_bleu_sent
                                    # Accuracy
                                    c_acc, w_acc = get_sentence_accuracy_scores_mustshe_debug(raw_path, pred_path, ref, gender_set, f, sl, tl, pl=None)
                                    results["accuracy"][translation]["total"][gender_set]["correct_ref"][lset] = np.array(c_acc)
                                    results["accuracy"][translation]["total"][gender_set]["wrong_ref"][lset] = np.array(w_acc)
                                else:
                                    continue
                            else:
                                # not zero-shot direction
                                continue
                else:
                    # pivot
                    for f in os.listdir(f"{pred_path}/pivot/{ref}/{gender_set}"):
                        if os.path.isfile(os.path.join(f"{pred_path}/pivot/{ref}/{gender_set}", f)):
                            lset = re.search(r"[a-z][a-z]-[a-z][a-z]-[a-z][a-z]", os.path.basename(f)).group(0)
                            sl = lset.split("-")[0]
                            pl = lset.split("-")[1]
                            tl = lset.split("-")[2]
                            lset = f"{sl}-{tl}"
                            
                            if sl != pl and tl != pl:
                                # if sl in ["fr", "it"] and tl in ["fr", "it"]:
                                if sl in ["it"] and tl in ["fr"]:
                                # if sl in ["fr"] and tl in ["it"]:
                                    # zero-shot direction
                                    if f.endswith(".pt"):
                                        # print(lset)
                                        print()
                                        print(translation, lset)
                                        # BLEU
                                        hypotheses = open(f"{pred_path}/pivot/{ref}/{gender_set}/{f}").readlines()
                                        c_references = open(f"{raw_path}/correct_ref/{gender_set}/{sl}-{tl}.t").readlines()
                                        w_references = open(f"{raw_path}/wrong_ref/{gender_set}/{sl}-{tl}.t").readlines()
                                        c_bleu_sent, w_bleu_sent = get_sentence_bleu_scores_mustshe(c_references, w_references, hypotheses)
                                        results["BLEU"][translation][gender_set]["correct_ref"][lset] = c_bleu_sent
                                        results["BLEU"][translation][gender_set]["wrong_ref"][lset] = w_bleu_sent
                                        # Accuracy
                                        c_acc, w_acc = get_sentence_accuracy_scores_mustshe_debug(raw_path, pred_path, ref, gender_set, f, sl, tl, pl)
                                        results["accuracy"][translation]["total"][gender_set]["correct_ref"][lset] = np.array(c_acc)
                                        results["accuracy"][translation]["total"][gender_set]["wrong_ref"][lset] = np.array(w_acc)
                                    else:
                                        continue
                            else:
                                # not zero-shot direction
                                continue

    for translation in ["zero_shot", "pivot"]:
    # for translation in ["zero_shot"]:
        bleu_dif = [] # TODO
        acc_dif = []
        # for gender_set in ["all", "feminine", "masculine"]:
        for ref in ["correct_ref"]: #, "wrong_ref"]:
            for gender_set in ["feminine"]:
                for lset in results["BLEU"][translation][gender_set][ref]:
                    bleu_dif = [] # TODO
                    acc_dif = []

                    cor_bleu = results["BLEU"][translation][gender_set]["correct_ref"][lset]
                    wro_bleu = results["BLEU"][translation][gender_set]["wrong_ref"][lset]
                    dif_bleu = cor_bleu - wro_bleu
                    results["BLEU"][translation][gender_set]["diff_c_w"][lset] = dif_bleu
                    bleu_dif.append(dif_bleu)
                    
                    cor_acc = results["accuracy"][translation]["total"][gender_set]["correct_ref"][lset]
                    wro_acc = results["accuracy"][translation]["total"][gender_set]["wrong_ref"][lset]
                    dif_acc = cor_acc - wro_acc
                    results["accuracy"][translation]["total"][gender_set]["diff_c_w"][lset] = dif_acc
                    acc_dif.append(dif_acc)

                    # if lset == "it-fr" or lset == "fr-it":
                    if lset == "it-fr":
                    # if lset == "fr-it":
                        print("'''''''''''''''''''''''''''")
                        # print(lset)
                        print(translation, lset, "dif")
                        print(dif_bleu[IDX], dif_acc[IDX])

                        b_indices = np.where(dif_bleu > 0)[0]
                        b_indices_s = np.where(dif_bleu < 0)[0]
                        a_indices = np.where(dif_acc < 0)[0]
                        a_indices_l = np.where(dif_acc > 0)[0]

                        print(set(b_indices.tolist()) & set(a_indices.tolist()))
                        print("bleu:", dif_bleu[list(set(b_indices.tolist()) & set(a_indices.tolist()))], "acc:", dif_acc[list(set(b_indices.tolist()) & set(a_indices.tolist()))])
                        print(set(b_indices_s.tolist()) & set(a_indices_l.tolist()))
                        print("'''''''''''''''''''''''''''")

                        # print(np.mean(dif_bleu)) #dif_acc[dif_acc < 0])
                        # print(np.mean(dif_acc)) #dif_acc[dif_acc < 0])

    return results

def main_mustshe(sentence_level=False):

    opt = parser.parse_args()
    raw_path = opt.raw_path
    pred_path = opt.pred_path
    train_set = opt.train_set
    out_path = opt.out_path
    out_path_csv = opt.out_path_csv
    out_path_json = opt.out_path_json
    df_path = opt.df_path
    
    results = get_empty_results_dict()
    if not sentence_level:
        results = calc_and_store_results_per_lset(results, raw_path, pred_path)
        results = calc_and_store_results_avg_zeroshot_directions(results, raw_path, pred_path)
        # results = calc_and_store_results_avg_supervised_directions(results, raw_path, pred_path, train_set)
    else:
        results = sent_level_calc_and_store_results_per_lset_debug(results, raw_path, pred_path)

    if not sentence_level:
        # export results
        # (1) all
        with open(f"{out_path}/json/{train_set}.json", 'w') as file:
            file.write(json.dumps(results, indent=3)) # use `json.loads` to do the reverse

        map_train_set_model_name = {
            "twoway.r32.q": "baseline_EN",
            "twoway.r32.q.new": "residual_EN",
            "twoway.SIM": "baseline_EN_AUX",
            "twoway.SIM.r32.q": "residual_EN_AUX",
            "twoway.new.ADV": "baseline_EN_ADV",
            "twoway.new.ADV.r32.q": "residual_EN_ADV",

            "twoway.ADV.GEN": "baseline_EN_ADV",
            "twoway.ADV.GEN.r32.q": "residual_EN_ADV",

            "twowayES": "baseline_ES",
            "twowayES.r32.q": "residual_ES",
            "twowayES.SIM": "baseline_ES_AUX",
            "twowayES.SIM.r32.q": "residual_ES_AUX",
            "twowayES.new.ADV": "baseline_ES_ADV",
            "twowayES.new.ADV.r32.q": "residual_ES_ADV",

            "twowayDE": "baseline_DE",
            "twowayDE.r32.q": "residual_DE",
            "twowayDE.SIM": "baseline_DE_AUX",
            "twowayDE.SIM.r32.q": "residual_DE_AUX",
            "twowayDE.new.ADV": "baseline_DE_ADV",
            "twowayDE.new.ADV.r32.q": "residual_DE_ADV",

            "multiwayEN": "small_baseline_EN",
            "multiwayEN.r32.q": "small_residual_EN",
            "multiwayEN.SIM": "small_baseline_EN_AUX",
            "multiwayEN.SIM.r32.q": "small_residual_EN_AUX",
            "multiwayEN.ADV": "small_baseline_EN_ADV",
            "multiwayEN.ADV.r32.q": "small_residual_EN_ADV",
        }

        # (2) BLEU
        out_path_bleu = f"{out_path_csv}/summary_bleu.csv"
        if os.path.exists(out_path_bleu):
            df_bleu = pd.read_csv(out_path_bleu, sep=";")
        else:
            with open(f"{df_path}/df_bleu.pkl", "rb") as file:
                df_bleu = pickle.load(file)

        # (3) Accuracy
        out_path_acc = f"{out_path_csv}/summary_acc.csv"
        if os.path.exists(out_path_acc):
            df_acc = pd.read_csv(out_path_acc, sep=";")
        else:
            with open(f"{df_path}/df_acc.pkl", "rb") as file:
                df_acc = pickle.load(file)

        # (4) Accuracy (cat)
        out_path_acc_cat = f"{out_path_csv}/summary_acc_cat.csv"
        if os.path.exists(out_path_acc_cat):
            df_acc_cat = pd.read_csv(out_path_acc_cat, sep=";")
        else:
            with open(f"{df_path}/df_acc_cat.pkl", "rb") as file:
                df_acc_cat = pickle.load(file)

        # (5) Accuracy (speaker)
        out_path_acc_speaker = f"{out_path_csv}/summary_acc_speaker.csv"
        if os.path.exists(out_path_acc_speaker):
            df_acc_speaker = pd.read_csv(out_path_acc_speaker, sep=";")
        else:
            with open(f"{df_path}/df_acc_speaker.pkl", "rb") as file:
                df_acc_speaker = pickle.load(file)

        # (6) Accuracy (speaker + cat. 1)
        out_path_acc_speaker_1 = f"{out_path_csv}/summary_acc_speaker_1.csv"
        if os.path.exists(out_path_acc_speaker):
            df_acc_speaker_1 = pd.read_csv(out_path_acc_speaker_1, sep=";")
        else:
            with open(f"{df_path}/df_acc_speaker.pkl", "rb") as file:
                df_acc_speaker_1 = pickle.load(file)
        # (6) Accuracy (speaker + cat. 2)
        out_path_acc_speaker_2 = f"{out_path_csv}/summary_acc_speaker_2.csv"
        if os.path.exists(out_path_acc_speaker):
            df_acc_speaker_2 = pd.read_csv(out_path_acc_speaker_2, sep=";")
        else:
            with open(f"{df_path}/df_acc_speaker.pkl", "rb") as file:
                df_acc_speaker_2 = pickle.load(file)

        
        incl_avg_sv = False # whether to compute average results for supervised directions
        export_results(results, "BLEU", df_bleu, out_path_bleu, map_train_set_model_name, train_set, avg_sv=incl_avg_sv)
        export_results(results, "accuracy", df_acc, out_path_acc, map_train_set_model_name, train_set, acc_type="total", avg_sv=incl_avg_sv)
        export_results(results, "accuracy", df_acc_cat, out_path_acc_cat, map_train_set_model_name, train_set, acc_type="1", avg_sv=incl_avg_sv)
        export_results(results, "accuracy", df_acc_speaker, out_path_acc_speaker, map_train_set_model_name, train_set, acc_type="female_speaker", avg_sv=incl_avg_sv)
        export_results(results, "accuracy", df_acc_speaker_1, out_path_acc_speaker_1, map_train_set_model_name, train_set, acc_type="female_speaker_1", avg_sv=incl_avg_sv)
        export_results(results, "accuracy", df_acc_speaker_2, out_path_acc_speaker_2, map_train_set_model_name, train_set, acc_type="female_speaker_2", avg_sv=incl_avg_sv)

if __name__ == "__main__":
    main_mustshe(sentence_level=False)
