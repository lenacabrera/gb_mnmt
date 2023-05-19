import os
import csv
import sys
from enum import Enum


correct = {

    "fr": {
        "remove": "Quand ces gens ont regardé qui était le meilleur plieur de protéines au monde, ce n'était pas un professeur du MIT, ce n'était pas un étudiant de Caltech, c'était une personne d'Angleterre, de Manchester, un femme qui, pendant la journée, était assistant de direction dans une clinique de sevrage, et qui la nuit était le meilleur plieur de protéines au monde."
    }
    

}


class MODE(Enum):
    PARA_ID = 0  # parallel data, keep only identical sentences from orig data files
    PARA_POSTPROC = 1  # parallel data, non-identical sentences with same content are made identical (post-processed)
    NONPARA = 2  # non-parallel data, preprocess for each monolingual file separately


def extract_from_tsv(data_dir_path, correct_ref_dir_name, wrong_ref_dir_name):

    mode = MODE.PARA_ID
    print("mode: ", mode.name)

    file_path = data_dir_path
    c_ref_dir = file_path + correct_ref_dir_name + "/"
    w_ref_dir = file_path + wrong_ref_dir_name + "/"

    tsv_file_es = open(os.path.join(file_path, "tsv/", "MONOLINGUAL.es_v1.2.tsv"), encoding='utf-8')
    tsv_file_fr = open(os.path.join(file_path, "tsv/", "MONOLINGUAL.fr_v1.2.tsv"), encoding='utf-8')
    tsv_file_it = open(os.path.join(file_path, "tsv/", "MONOLINGUAL.it_v1.2.tsv"), encoding='utf-8')

    map_es = create_dict(mode, tsv_file_es, c_ref_dir, w_ref_dir, sl="en", tl="es")
    map_fr = create_dict(mode, tsv_file_fr, c_ref_dir, w_ref_dir, sl="en", tl="fr")
    map_it = create_dict(mode, tsv_file_it, c_ref_dir, w_ref_dir, sl="en", tl="it")

    # all
    if "PAR" in mode.name:
        with open(os.path.join(file_path, "tsv/", "MULTILINGUAL_v1.2.tsv"), encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter="\t")
            # skip header (IT;FR;ES;CATEGORY)
            csv_reader.__next__()

            par_es_c = open(os.path.join(c_ref_dir, "es_par.s"), "w", encoding='utf-8')
            par_it_c = open(os.path.join(c_ref_dir, "it_par.s"), "w", encoding='utf-8')
            par_fr_c = open(os.path.join(c_ref_dir, "fr_par.s"), "w", encoding='utf-8')
            par_en_c = open(os.path.join(c_ref_dir, "en_par.s"), "w", encoding='utf-8')

            par_es_w = open(os.path.join(w_ref_dir, "es_par.s"), "w", encoding='utf-8')
            par_it_w = open(os.path.join(w_ref_dir, "it_par.s"), "w", encoding='utf-8')
            par_fr_w = open(os.path.join(w_ref_dir, "fr_par.s"), "w", encoding='utf-8')
            par_en_w = open(os.path.join(w_ref_dir, "en_par.s"), "w", encoding='utf-8')

            es_add_info = open(os.path.join(file_path, "es_add.csv"), "w", encoding='utf-8')
            fr_add_info = open(os.path.join(file_path, "fr_add.csv"), "w", encoding='utf-8')
            it_add_info = open(os.path.join(file_path, "it_add.csv"), "w", encoding='utf-8')

            es_speaker_c = open(os.path.join(c_ref_dir, "es_speaker.csv"), "w", encoding='utf-8')
            es_speaker_w = open(os.path.join(w_ref_dir, "es_speaker.csv"), "w", encoding='utf-8')
            fr_speaker_c = open(os.path.join(c_ref_dir, "fr_speaker.csv"), "w", encoding='utf-8')
            fr_speaker_w = open(os.path.join(w_ref_dir, "fr_speaker.csv"), "w", encoding='utf-8')
            it_speaker_c = open(os.path.join(c_ref_dir, "it_speaker.csv"), "w", encoding='utf-8')
            it_speaker_w = open(os.path.join(w_ref_dir, "it_speaker.csv"), "w", encoding='utf-8')

            es_category_c = open(os.path.join(c_ref_dir, "es_category.csv"), "w", encoding='utf-8')
            es_category_w = open(os.path.join(w_ref_dir, "es_category.csv"), "w", encoding='utf-8')
            fr_category_c = open(os.path.join(c_ref_dir, "fr_category.csv"), "w", encoding='utf-8')
            fr_category_w = open(os.path.join(w_ref_dir, "fr_category.csv"), "w", encoding='utf-8')
            it_category_c = open(os.path.join(c_ref_dir, "it_category.csv"), "w", encoding='utf-8')
            it_category_w = open(os.path.join(w_ref_dir, "it_category.csv"), "w", encoding='utf-8')

            es_gterms_c = open(os.path.join(c_ref_dir, "es_gterms.csv"), "w", encoding='utf-8')
            es_gterms_w = open(os.path.join(w_ref_dir, "es_gterms.csv"), "w", encoding='utf-8')
            fr_gterms_c = open(os.path.join(c_ref_dir, "fr_gterms.csv"), "w", encoding='utf-8')
            fr_gterms_w = open(os.path.join(w_ref_dir, "fr_gterms.csv"), "w", encoding='utf-8')
            it_gterms_c = open(os.path.join(c_ref_dir, "it_gterms.csv"), "w", encoding='utf-8')
            it_gterms_w = open(os.path.join(w_ref_dir, "it_gterms.csv"), "w", encoding='utf-8')
            
            for row in csv_reader:
                it_id = row[0]
                fr_id = row[1]
                es_id = row[2]

                if it_id == "NULL" or fr_id == "NULL" or es_id == "NULL":
                    continue
                else:
                    if es_id in map_es:
                        if it_id in map_it:
                            if fr_id in map_fr:
                                es_src = map_es[es_id][0]
                                it_src = map_it[it_id][0]
                                fr_src = map_fr[fr_id][0]
                            else:
                                continue

                    if es_src == it_src == fr_src:
                        par_es_c.write(map_es[es_id][1] + "\n")
                        par_it_c.write(map_it[it_id][1] + "\n")
                        par_fr_c.write(map_fr[fr_id][1] + "\n")
                        par_en_c.write(es_src + "\n")

                        par_es_w.write(map_es[es_id][2] + "\n")
                        par_it_w.write(map_it[it_id][2] + "\n")
                        par_fr_w.write(map_fr[fr_id][2] + "\n")
                        par_en_w.write(es_src + "\n")

                        es_speaker_c.write(map_es[es_id][3] + "\n")
                        es_speaker_w.write(map_es[es_id][3] + "\n")
                        es_category_c.write(map_es[es_id][4] + "\n")
                        es_category_w.write(map_es[es_id][4] + "\n")
                        terms = map_es[es_id][5].split(";")
                        for term in terms:
                            es_gterms_c.write(term.split(" ")[0] + " ")
                            es_gterms_w.write(term.split(" ")[1] + " ")
                        es_gterms_c.write("\n")
                        es_gterms_w.write("\n")

                        it_speaker_c.write(map_it[it_id][3] + "\n")
                        it_speaker_w.write(map_it[it_id][3] + "\n")
                        it_category_c.write(map_it[it_id][4] + "\n")
                        it_category_w.write(map_it[it_id][4] + "\n")
                        terms = map_it[it_id][5].split(";")
                        for term in terms:
                            it_gterms_c.write(term.split(" ")[0] + " ")
                            it_gterms_w.write(term.split(" ")[1] + " ")
                        it_gterms_c.write("\n")
                        it_gterms_w.write("\n")

                        fr_speaker_c.write(map_fr[fr_id][3] + "\n")
                        fr_speaker_w.write(map_fr[fr_id][3] + "\n")
                        fr_category_c.write(map_fr[fr_id][4] + "\n")
                        fr_category_w.write(map_fr[fr_id][4] + "\n")
                        terms = map_fr[fr_id][5].split(";")
                        for term in terms:
                            fr_gterms_c.write(term.split(" ")[0] + " ")
                            fr_gterms_w.write(term.split(" ")[1] + " ")
                        fr_gterms_c.write("\n")
                        fr_gterms_w.write("\n")
                    else:
                        if mode.name == MODE.PARA_ID.name:
                            continue
                        elif mode.name == MODE.PARA_POSTPROC.name:
                            print("TODO: post-processing")
                        else:
                            pass


def create_dict(mode, in_file, c_ref_dir, w_ref_dir, sl, tl):
    read_tsv_tl = csv.reader(in_file, delimiter="\t")
    next(read_tsv_tl)

    map_tl = {}

    if mode.name == MODE.NONPARA.name:
        sl_tl_c = open(c_ref_dir + f"{sl}-{tl}.{sl}", "w", encoding='utf-8')
        tl_sl_c = open(c_ref_dir + f"{tl}-{sl}.{tl}", "w", encoding='utf-8')
        sl_tl_w = open(w_ref_dir + f"{sl}-{tl}.{sl}", "w", encoding='utf-8')
        tl_sl_w = open(w_ref_dir + f"{tl}-{sl}.{tl}", "w", encoding='utf-8')

    for row in read_tsv_tl:
        src = row[4]
        ref = row[5]

        ref_wrong = row[6]

        if tl == "fr":
            if ref_wrong in correct["fr"]["remove"]:
                # skip this, as wrong ref. is faulty in orig. MuST-SHE
                continue

        speaker_gender = row[8]
        category = row[9]
        gender_terms = row[12]
        map_tl[row[0]] = [src, ref, ref_wrong, speaker_gender, category, gender_terms]
        if mode.name == MODE.NONPARA.name:
            sl_tl_c.write(src + '\n')
            tl_sl_c.write(ref + '\n')
            sl_tl_w.write(src + '\n')
            tl_sl_w.write(ref_wrong + '\n')

    return map_tl


if __name__ == '__main__':
    args = sys.argv[1:]
    extract_from_tsv(args[0], args[1], args[2])
