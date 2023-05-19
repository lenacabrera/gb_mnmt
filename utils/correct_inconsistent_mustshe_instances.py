import numpy as np
import json
import sys
import os
import argparse
import re
import pandas as pd
import pickle
import os

np.seterr('raise')

parser = argparse.ArgumentParser(description='prep_results.py')

parser.add_argument('-raw_path', required=True, default=None)

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


def corrrect_fr(tref, op_tref, gterms):
    return



def check_correctness_of_gender_terms(raw_path, ref, gender_set, f, sl, tl, pl):

    l = tl

    gterms_file = open(f"{raw_path}/{ref}/{gender_set}/annotation/{l}_gterms.csv", "r", encoding="utf-8")

    # target reference file (correct/wrong)
    tref_file = open(f"{raw_path}/{ref}/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")
    # opposite target reference
    if ref == "correct_ref":
        op_tref_file = open(f"{raw_path}/wrong_ref/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")
    else:
        op_tref_file = open(f"{raw_path}/correct_ref/{gender_set}/{sl}-{tl}.t", "r", encoding="utf-8")

    for tref, op_tref, gterms in zip(tref_file, op_tref_file, gterms_file):

        tref_ = tref.strip()
        op_tref_ = op_tref.strip()
        gterms_list = gterms.split()

        # correct reference
        if tref_ in [e.strip() for e in corrected_references[l].keys()]:
            tref = corrected_references[l][tref_]
        if op_tref_ in [e.strip() for e in corrected_references[l].keys()]:
            op_tref = corrected_references[l][op_tref_]

        if tref_ in [e.strip() for e in corrected_gterms[l].keys()]:
            # correct gender terms
            gterms_list = corrected_gterms[l][tref_].split()
            print("corrected gterms_list: ", gterms_list)
        punctuation_marks = [".", ",", "!", "?", ":", ";", "¿", "¡", "\"", "\n", "(", ")", "...", "—", "«", "»"] #, "-", "'"]
        for p_mark in punctuation_marks:
            tref = tref.replace(p_mark, " ")
            op_tref = op_tref.replace(p_mark, " ")
            # gterms = gterms.replace(p_mark, " ")

        tref_list = tref.split()
        op_tref_list = op_tref.split()


        keep_expr = ["un", "une", "una", "l", "qu"]

        tref_list_ = []
        for t in tref_list:
            split_tok = re.split('\'', t)
            if len(split_tok) > 1:
                for keep in keep_expr:
                    if keep in split_tok:
                        split_tok[0] += "'"
                        for st in split_tok:
                            tref_list_.append(st)
                    else:
                        tref_list_.append(t)
            else:
                tref_list_.append(t)

        op_tref_list_ = []
        for t in op_tref_list:
            split_tok = re.split('\'', t)
            if len(split_tok) > 1:
                for keep in keep_expr:
                    if keep in split_tok:
                        split_tok[0] += "'"
                        for st in split_tok:
                            op_tref_list_.append(st)
                    else:
                        op_tref_list_.append(t)
            else:
                op_tref_list_.append(t)

        tref_list = tref_list_
        op_tref_list = op_tref_list_

        g_w_indices = []
        for i, (tw, otw) in enumerate(zip(tref_list, op_tref_list)):
            # check where correct and wrong ref. differ and store word index
            if tw != otw:
                g_w_indices.append(i)

        if len(g_w_indices) != len(gterms_list):
            print(tref_list)
            print(op_tref_list)
            print(len(g_w_indices))
            print(gterms_list)

        # check correct gterm with pred. words ~ gterm pos. idx.
        n_forward, n_backward = 2, 2  # buffer around orig. gterm pos. idx.
        pred_gterms = []
        for i, gterm in enumerate(gterms_list):
            if len(g_w_indices) > 0:
                idx = g_w_indices[i]
                # if gterm in pred_list[idx-n_backward:idx+n_forward]:
                #     pred_gterms.append(gterm)
            # else:
                # if gterm in pred_list:
                #     pred_gterms.append(gterm)
        print("---")
      
    
if __name__ == "__main__":
    opt = parser.parse_args()
    raw_path = opt.raw_path

    for gender_set in ["all", "feminine", "masculine"]:
        for ref in ["correct_ref", "wrong_ref"]:
            for f in os.listdir(f"{raw_path}/{ref}/{gender_set}"):
                if os.path.isfile(os.path.join(f"{raw_path}/{ref}/{gender_set}", f)):  # to catch 'annotation' directory
                    lset = re.search(r"[a-z][a-z]-[a-z][a-z]", os.path.basename(f)).group(0)
                    sl = lset.split("-")[0]
                    tl = lset.split("-")[1]
                    if tl != "en":
                        check_correctness_of_gender_terms(raw_path, ref, gender_set, f, sl, tl, pl=None)
