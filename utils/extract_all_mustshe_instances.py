from ctypes import alignment
from fileinput import close
import os
import csv
import sys
import argparse
import tqdm
import random
from mosestokenizer import MosesTokenizer

random.seed(0)

parser = argparse.ArgumentParser(description='extract_train_from_mustshe.py')
parser.add_argument('-data_dir_path', required=True, default=None)

def extract_train_set_from_tsv():

    opt = parser.parse_args()
    file_path = opt.data_dir_path

    out_path = file_path

    tsv_file_es = open(os.path.join(file_path, "tsv/", "MONOLINGUAL.es_v1.2.tsv"), encoding='utf-8')
    tsv_file_fr = open(os.path.join(file_path, "tsv/", "MONOLINGUAL.fr_v1.2.tsv"), encoding='utf-8')
    tsv_file_it = open(os.path.join(file_path, "tsv/", "MONOLINGUAL.it_v1.2.tsv"), encoding='utf-8')

    map_es = create_language_pair_dict_with_add_info(tsv_file_es)
    map_fr = create_language_pair_dict_with_add_info(tsv_file_fr)
    map_it = create_language_pair_dict_with_add_info(tsv_file_it)

    mustshe_exclude_path = file_path + "/correct_ref/"

    for gender_set in ["all", "feminine", "masculine"]:
        es_ex_file = open(os.path.join(mustshe_exclude_path, gender_set, "es-en.s"), encoding='utf-8')
        en_es_ex_file = open(os.path.join(mustshe_exclude_path, gender_set, "es-en.t"), encoding='utf-8')
        fr_ex_file = open(os.path.join(mustshe_exclude_path, gender_set, "fr-en.s"), encoding='utf-8')
        en_fr_ex_file = open(os.path.join(mustshe_exclude_path, gender_set, "fr-en.t"), encoding='utf-8')
        it_ex_file = open(os.path.join(mustshe_exclude_path, gender_set, "it-en.s"), encoding='utf-8')
        en_it_ex_file = open(os.path.join(mustshe_exclude_path, gender_set, "it-en.t"), encoding='utf-8')

        map_es_ex = create_language_pair_dict(en_es_ex_file, es_ex_file)
        map_fr_ex = create_language_pair_dict(en_fr_ex_file, fr_ex_file)
        map_it_ex = create_language_pair_dict(en_it_ex_file, it_ex_file)
    
        map_es_cleaned = remove_test_instances(map_es_ex, map_es[gender_set])
        map_fr_cleaned = remove_test_instances(map_fr_ex, map_fr[gender_set])
        map_it_cleaned = remove_test_instances(map_it_ex, map_it[gender_set])

        map_es_final, es_val_indices = export_train_instances(map_es_cleaned, sl="en", tl="es", out_path=out_path, gender_set=gender_set)
        map_fr_final, fr_val_indices = export_train_instances(map_fr_cleaned, sl="en", tl="fr", out_path=out_path, gender_set=gender_set)
        map_it_final, it_val_indices = export_train_instances(map_it_cleaned, sl="en", tl="it", out_path=out_path, gender_set=gender_set)
    
    return map_es_final, map_fr_final, map_it_final, es_val_indices, fr_val_indices, it_val_indices


def create_language_pair_dict_with_add_info(in_file):
    read_tsv_tl = csv.reader(in_file, delimiter="\t")
    next(read_tsv_tl)
    map_tl = {
        "all": {
            "src": [],
            "ref": [],
            "speaker": [],
            "category": [],
            "gterms": [],
            "gender_sentence_label": [],
            "gender_word_labels": [],
            "gender_tok_labels": []
        },
        "feminine": {
            "src": [],
            "ref": [],
            "speaker": [],
            "category": [],
            "gterms": [],
            "gender_sentence_label": [],
            "gender_word_labels": [],
            "gender_tok_labels": []
        },
        "masculine": {
            "src": [],
            "ref": [],
            "speaker": [],
            "category": [],
            "gterms": [],
            "gender_sentence_label": [],
            "gender_word_labels": [],
            "gender_tok_labels": []
        }
    }

    for row in read_tsv_tl:
        src = row[4]
        ref = row[5]
        speaker_gender = row[8]
        category = row[9]
        gender_terms = row[12].split(';')

        gender_terms_cr = []
        for gt in gender_terms:
            cr_wr = gt.split(' ')
            gender_terms_cr.append(cr_wr[0])

        # note, all below are 'correct_ref'
        map_tl["all"]["src"].append(src)
        map_tl["all"]["ref"].append(ref)
        map_tl["all"]["speaker"].append(speaker_gender)
        map_tl["all"]["category"].append(category)
        map_tl["all"]["gterms"].append(gender_terms_cr)

        if "F" in category:
            map_tl["feminine"]["src"].append(src)
            map_tl["feminine"]["ref"].append(ref)
            map_tl["feminine"]["speaker"].append(speaker_gender)
            map_tl["feminine"]["category"].append(category)
            map_tl["feminine"]["gterms"].append(gender_terms_cr)
            map_tl["feminine"]["gender_sentence_label"].append('2') # 'f'
            map_tl["all"]["gender_sentence_label"].append('2')  # 'f'
        
        if "M" in category:
            map_tl["masculine"]["src"].append(src)
            map_tl["masculine"]["ref"].append(ref)
            map_tl["masculine"]["speaker"].append(speaker_gender)
            map_tl["masculine"]["category"].append(category)
            map_tl["masculine"]["gterms"].append(gender_terms_cr)
            map_tl["masculine"]["gender_sentence_label"].append('1') # 'm'
            map_tl["all"]["gender_sentence_label"].append('1') # 'm'

    return map_tl


def create_language_pair_dict(sl_file, tl_file):
    map_sl_tl = dict(zip(sl_file, tl_file))
    return map_sl_tl


def remove_test_instances(en_tl_ex, en_tl):
    for en in en_tl_ex.keys():
        if en in en_tl["src"]:
            idx = en_tl["src"].index(en)
            del en_tl["src"][idx]
            del en_tl["ref"][idx]
            del en_tl["speaker"][idx]
            del en_tl["category"][idx]
            del en_tl["gterms"][idx]
            del en_tl["gender_sentence_label"][idx]
    return en_tl
    

def export_train_instances(map, sl, tl, out_path, gender_set):

    map = word_level_gender_labels(map)

    # train/valid split
    num_valid = round(len(map["src"]) * 0.075)

    valid_indices = list(range(0, len(map["src"])-1))
    random.shuffle(valid_indices)
    valid_indices = valid_indices[:num_valid]

    sl_out_file = open(os.path.join(out_path, f"train/{gender_set}/{sl}-{tl}.s"), "w", encoding='utf-8')
    tl_out_file = open(os.path.join(out_path, f"train/{gender_set}/{tl}-{sl}.s"), "w", encoding='utf-8')

    gndr_out_file = open(os.path.join(out_path, f"train/{gender_set}/gen_label/sent/{tl}.s"), "w", encoding='utf-8') # sentence gender label
    gndr_labels_out_file = open(os.path.join(out_path, f"train/{gender_set}/gen_label/word/{tl}.s"), "w", encoding='utf-8') # word gender labels
    gndr_tok_labels_out_file = open(os.path.join(out_path, f"train/{gender_set}/gen_label/tok/{tl}.s"), "w", encoding='utf-8') # word gender labels

    sl_out_file_v = open(os.path.join(out_path, f"valid/{gender_set}/{sl}-{tl}.s"), "w", encoding='utf-8')
    tl_out_file_v = open(os.path.join(out_path, f"valid/{gender_set}/{tl}-{sl}.s"), "w", encoding='utf-8')

    gndr_out_file_v = open(os.path.join(out_path, f"valid/{gender_set}/gen_label/sent/{tl}.s"), "w", encoding='utf-8') # sentence gender label
    gndr_labels_out_file_v = open(os.path.join(out_path, f"valid/{gender_set}/gen_label/word/{tl}.s"), "w", encoding='utf-8')  # word gender labels
    gndr_tok_labels_out_file_v = open(os.path.join(out_path, f"valid/{gender_set}/gen_label/tok/{tl}.s"), "w", encoding='utf-8')  # word gender labels

    for i, sl in enumerate(map["src"]):
        if i in valid_indices:
            sl_out_file_v.write(sl + '\n')
        else:
            sl_out_file.write(sl + '\n')
    for i, tl in enumerate(map["ref"]):
        if i in valid_indices:
            tl_out_file_v.write(tl + '\n')
        else:
            tl_out_file.write(tl + '\n')
    for i, gndr in enumerate(map["gender_sentence_label"]):
        if i in valid_indices:
            gndr_out_file_v.write(gndr + '\n')
        else:
            gndr_out_file.write(gndr + '\n')
    for i, gndr in enumerate(map["gender_word_labels"]):
        if i in valid_indices:
            gndr_labels_out_file_v.write(gndr + '\n')
        else:
            gndr_labels_out_file.write(gndr + '\n')

    return map, valid_indices

def word_level_gender_labels(map):

    n_macsuline = 0
    n_feminine = 0
    for i, sentence in enumerate(map["ref"]):
        word_labels = ""
        words = sentence.split()
        for j, word in enumerate(words):
            punctuation_marks = [".", ",", "!", "?", ":", ";", "¿", "¡", "\"", "\n"]
            for mark in punctuation_marks:
                word = word.replace(mark, "")
            word_label = "0" # neuter
            if word in map["gterms"][i]:
                gender = map["category"][i][1]
                if gender == "M":
                    # masculine
                    word_label = "1"
                    n_macsuline += 1
                else:
                    # feminine
                    word_label = "2"
                    n_feminine += 1
            
            word_labels += word_label
            if j < len(words) - 1:
                word_labels += " "
        map["gender_word_labels"].append(word_labels)

    print(f"In this gender set: {n_macsuline} masculine and {n_feminine} feminine words.")

    return map

def create_multiway_train_set(map_es, map_fr, map_it, es_val_indices, fr_val_indices, it_val_indices):

    it_fr = {
        "it": {
            "ref": [],
            "speaker": [],
            "category": [],
            "gterms": [],
            "gender_sentence_label": [],
            "gender_word_labels": [],
            "gender_tok_labels": []
        },
        "fr": {
            "ref": [],
            "speaker": [],
            "category": [],
            "gterms": [],
            "gender_sentence_label": [],
            "gender_word_labels": [],
            "gender_tok_labels": []
        }
    }

    for i, s_en in enumerate(map_it["all"]["src"]):
        if s_en in map_fr["all"]["src"]:
            it_fr["it"]["ref"].append(map_it["all"]["ref"][i])
            it_fr["it"]["speaker"].append(map_it["all"]["speaker"][i])
            it_fr["it"]["category"].append(map_it["all"]["category"][i])
            it_fr["it"]["gterms"].append(map_it["all"]["gterms"][i])
            it_fr["it"]["gender_sentence_label"].append(map_it["all"]["gender_sentence_label"][i])
            it_fr["it"]["gender_word_labels"].append(map_it["all"]["gender_word_labels"][i])
            it_fr["it"]["gender_tok_labels"].append(map_it["all"]["gender_tok_labels"][i])

            j = map_fr["all"]["ref"].index(s_en)
            it_fr["fr"]["ref"].append(map_fr["all"]["ref"][j])
            it_fr["fr"]["speaker"].append(map_fr["all"]["speaker"][j])
            it_fr["fr"]["category"].append(map_fr["all"]["category"][j])
            it_fr["fr"]["gterms"].append(map_fr["all"]["gterms"][j])
            it_fr["fr"]["gender_sentence_label"].append(map_fr["all"]["gender_sentence_label"][j])
            it_fr["fr"]["gender_word_labels"].append(map_fr["all"]["gender_word_labels"][j])
            it_fr["fr"]["gender_tok_labels"].append(map_fr["all"]["gender_tok_labels"][j])

    opt = parser.parse_args()
    out_path = opt.data_dir_path

    sl_out_file = open(os.path.join(out_path, f"train/all/{sl}-{tl}.s"), "w", encoding='utf-8')
    tl_out_file = open(os.path.join(out_path, f"train/all/{tl}-{sl}.s"), "w", encoding='utf-8')

    gndr_out_file = open(os.path.join(out_path, f"train/all/gen_label/sent/{tl}.s"), "w", encoding='utf-8') # sentence gender label
    gndr_labels_out_file = open(os.path.join(out_path, f"train/all/gen_label/word/{tl}.s"), "w", encoding='utf-8') # word gender labels
    gndr_tok_labels_out_file = open(os.path.join(out_path, f"train/all/gen_label/tok/{tl}.s"), "w", encoding='utf-8') # word gender labels

    sl_out_file_v = open(os.path.join(out_path, f"valid/all/{sl}-{tl}.s"), "w", encoding='utf-8')
    tl_out_file_v = open(os.path.join(out_path, f"valid/all/{tl}-{sl}.s"), "w", encoding='utf-8')

    gndr_out_file_v = open(os.path.join(out_path, f"valid/all/gen_label/sent/{tl}.s"), "w", encoding='utf-8') # sentence gender label
    gndr_labels_out_file_v = open(os.path.join(out_path, f"valid/all/gen_label/word/{tl}.s"), "w", encoding='utf-8')  # word gender labels
    gndr_tok_labels_out_file_v = open(os.path.join(out_path, f"valid/all/gen_label/tok/{tl}.s"), "w", encoding='utf-8')  # word gender labels

    for i, sl in enumerate(map_es["src"]):
        if i in es_val_indices:
            sl_out_file_v.write(sl + '\n')
        else:
            sl_out_file.write(sl + '\n')
    for i, tl in enumerate(map_es["ref"]):
        if i in es_val_indices:
            tl_out_file_v.write(tl + '\n')
        else:
            tl_out_file.write(tl + '\n')
    for i, gndr in enumerate(map_es["gender_sentence_label"]):
        if i in es_val_indices:
            gndr_out_file_v.write(gndr + '\n')
        else:
            gndr_out_file.write(gndr + '\n')
    for i, gndr in enumerate(map_es["gender_word_labels"]):
        if i in es_val_indices:
            gndr_labels_out_file_v.write(gndr + '\n')
        else:
            gndr_labels_out_file.write(gndr + '\n')


if __name__ == '__main__':
    map_es, map_fr, map_it = extract_train_set_from_tsv()
    create_multiway_train_set(map_es, map_fr, map_it)