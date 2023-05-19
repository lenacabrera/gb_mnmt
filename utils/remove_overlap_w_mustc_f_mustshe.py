import sys
import tqdm

def create_language_pair_dict(en, es, fr, it):
    with open(en, "r") as ef:
        with open(es, "r") as esf:
            with open(fr, "r") as frf:
                with open(it, "r") as itf:
                    en_lines = ef.read().splitlines()
                    es_lines = esf.read().splitlines()
                    fr_lines = frf.read().splitlines()
                    it_lines = itf.read().splitlines()

                    en_es_fr_it_d = {}
                    for l, es_l, fr_l, it_l in zip(en_lines, es_lines, fr_lines, it_lines):
                        en_es_fr_it_d[l] = {
                            "es": es_l,
                            "fr": fr_l,
                            "it": it_l,
                        }
                    return en_es_fr_it_d


def create_add_dict(en, es_add, fr_add, it_add):
    with open(en, "r") as ef:
        with open(es_add, "r") as es_add_f:
            with open(fr_add, "r") as fr_add_f:
                with open(it_add, "r") as it_add_f:
                    en_lines = ef.read().splitlines()
                    es_add_lines = es_add_f.read().splitlines()
                    fr_add_lines = fr_add_f.read().splitlines()
                    it_add_lines = it_add_f.read().splitlines()

                    en_add = {}
                    for l, el, fl, il in zip(en_lines, es_add_lines, fr_add_lines, it_add_lines):
                        en_add[l] = {
                            "es": el,
                            "fr": fl,
                            "it": il,
                        }
    return en_add


def create_add_info_dict(en, add):
    with open(en, "r") as ef:
        with open(add, "r") as addf:
            en_lines = ef.read().splitlines()
            add_lines = addf.read().splitlines()

            en_add = {}
            for l, add_l in zip(en_lines, add_lines):
                add_lines_sep = add_l.split(",")
                gender_speaker = add_lines_sep[0]
                category = add_lines_sep[1]
                gender_terms = add_lines_sep[2].split(';')
                gender_terms_cr = []
                gender_terms_wr = []
                for gt in gender_terms:
                    cr_wr = gt.split(' ')
                    gender_terms_cr.append(cr_wr[0])
                    gender_terms_wr.append(cr_wr[1])

                en_add[l] = {
                    "speaker_gender": gender_speaker,
                    "category": category,
                    "gender_terms_cr": gender_terms_cr,
                    "gender_terms_wr": gender_terms_wr,
                }
            return en_add

def create_list_of_en_mustc_sentences(en_cs_mustc, en_de_mustc, en_es_mustc, en_fr_mustc, en_it_mustc, en_nl_mustc, en_pt_mustc, en_ro_mustc, en_ru_mustc):
    with open(en_cs_mustc, "r") as en_cs:
        with open(en_de_mustc, "r") as en_de:
            with open(en_es_mustc, "r") as en_es:
                with open(en_fr_mustc, "r") as en_fr:
                    with open(en_it_mustc, "r") as en_it:
                        with open(en_nl_mustc, "r") as en_nl:  
                            with open(en_pt_mustc, "r") as en_pt:
                                with open(en_ro_mustc, "r") as en_ro:
                                    with open(en_ru_mustc, "r") as en_ru:
                                        en_cs_lines = en_cs.read().splitlines()
                                        en_de_lines = en_de.read().splitlines()
                                        en_es_lines = en_es.read().splitlines()
                                        en_fr_lines = en_fr.read().splitlines()
                                        en_it_lines = en_it.read().splitlines()
                                        en_nl_lines = en_nl.read().splitlines()
                                        en_pt_lines = en_pt.read().splitlines()
                                        en_ro_lines = en_ro.read().splitlines()
                                        en_ru_lines = en_ru.read().splitlines()
                                        lines = en_cs_lines
                                        lines.extend(en_de_lines)
                                        lines.extend(en_es_lines)
                                        lines.extend(en_fr_lines)
                                        lines.extend(en_it_lines)
                                        lines.extend(en_nl_lines)
                                        lines.extend(en_pt_lines)
                                        lines.extend(en_ro_lines)
                                        lines.extend(en_ru_lines)
    return lines

def check_overlap(en_cs_mustc, en_de_mustc, en_es_mustc, en_fr_mustc, en_it_mustc, en_nl_mustc, en_pt_mustc, en_ro_mustc, en_ru_mustc, en_par_mustshe, 
                  es_par_mustshe, fr_par_mustshe, it_par_mustshe, es_speaker_mustshe, es_category_mustshe, es_gterms_mustshe, fr_speaker_mustshe, fr_category_mustshe, fr_gterms_mustshe, it_speaker_mustshe, it_category_mustshe, it_gterms_mustshe,
                  es_wr_par_mustshe, fr_wr_par_mustshe, it_wr_par_mustshe, es_wr_speaker_mustshe, es_wr_category_mustshe, es_wr_gterms_mustshe, fr_wr_speaker_mustshe, fr_wr_category_mustshe, fr_wr_gterms_mustshe, it_wr_speaker_mustshe, it_wr_category_mustshe, it_wr_gterms_mustshe,
                  out_dir_cr, out_dir_wr):

    en = create_list_of_en_mustc_sentences(en_cs_mustc, en_de_mustc, en_es_mustc, en_fr_mustc, en_it_mustc, en_nl_mustc, en_pt_mustc, en_ro_mustc, en_ru_mustc)
    mustshe_en_es_fr_it_d = create_language_pair_dict(en_par_mustshe, es_par_mustshe, fr_par_mustshe, it_par_mustshe)
    mustshe_en_wr_es_fr_it_d = create_language_pair_dict(en_par_mustshe, es_wr_par_mustshe, fr_wr_par_mustshe, it_wr_par_mustshe)

    speaker = create_add_dict(en_par_mustshe, es_speaker_mustshe, fr_speaker_mustshe, it_speaker_mustshe)
    speaker_wr = create_add_dict(en_par_mustshe, es_wr_speaker_mustshe, fr_wr_speaker_mustshe, it_wr_speaker_mustshe)
    category = create_add_dict(en_par_mustshe, es_category_mustshe, fr_category_mustshe, it_category_mustshe)
    category_wr = create_add_dict(en_par_mustshe, es_wr_category_mustshe, fr_wr_category_mustshe, it_wr_category_mustshe)
    gterms = create_add_dict(en_par_mustshe, es_gterms_mustshe, fr_gterms_mustshe, it_gterms_mustshe)
    gterms_wr = create_add_dict(en_par_mustshe, es_wr_gterms_mustshe, fr_wr_gterms_mustshe, it_wr_gterms_mustshe)

    en_novl = []
    es_novl = []
    fr_novl = []
    it_novl = []
    es_wr_novl = []
    fr_wr_novl = []
    it_wr_novl = []

    ovl = []

    es_speaker_cr_novl = []
    es_speaker_wr_novl = []
    fr_speaker_cr_novl = []
    fr_speaker_wr_novl = []
    it_speaker_cr_novl = []
    it_speaker_wr_novl = []

    es_category_cr_novl = []
    es_category_wr_novl = []
    fr_category_cr_novl = []
    fr_category_wr_novl = []
    it_category_cr_novl = []
    it_category_wr_novl = []

    es_add_gterms_cr_novl = []
    es_add_gterms_wr_novl = []
    fr_add_gterms_cr_novl = []
    fr_add_gterms_wr_novl = []
    it_add_gterms_cr_novl = []
    it_add_gterms_wr_novl = []

    for l in tqdm.tqdm(mustshe_en_es_fr_it_d.keys()):
        if l in en:
            ovl.append(l)
        else:
            en_novl.append(l)

            es_novl.append(mustshe_en_es_fr_it_d[l]["es"])
            fr_novl.append(mustshe_en_es_fr_it_d[l]["fr"])
            it_novl.append(mustshe_en_es_fr_it_d[l]["it"]) 
            es_wr_novl.append(mustshe_en_wr_es_fr_it_d[l]["es"])
            fr_wr_novl.append(mustshe_en_wr_es_fr_it_d[l]["fr"])
            it_wr_novl.append(mustshe_en_wr_es_fr_it_d[l]["it"])

            es_speaker_cr_novl.append(speaker[l]["es"])
            fr_speaker_cr_novl.append(speaker[l]["fr"])
            it_speaker_cr_novl.append(speaker[l]["it"])
            es_speaker_wr_novl.append(speaker_wr[l]["es"])
            fr_speaker_wr_novl.append(speaker_wr[l]["fr"])
            it_speaker_wr_novl.append(speaker_wr[l]["it"])

            es_category_cr_novl.append(category[l]["es"])
            fr_category_cr_novl.append(category[l]["fr"])
            it_category_cr_novl.append(category[l]["it"])
            es_category_wr_novl.append(category_wr[l]["es"])
            fr_category_wr_novl.append(category_wr[l]["fr"])
            it_category_wr_novl.append(category_wr[l]["it"])

            es_add_gterms_cr_novl.append(gterms[l]["es"])
            fr_add_gterms_cr_novl.append(gterms[l]["fr"])
            it_add_gterms_cr_novl.append(gterms[l]["it"])
            es_add_gterms_wr_novl.append(gterms_wr[l]["es"])
            fr_add_gterms_wr_novl.append(gterms_wr[l]["fr"])
            it_add_gterms_wr_novl.append(gterms_wr[l]["it"])

    with open(out_dir_cr + "en_par.s", "w") as enf:
        with open(out_dir_wr + "en_par.s", "w") as enf_wr:
            for l in en_novl:
                enf.write(l + "\n")
                enf_wr.write(l + "\n")

    with open(out_dir_cr + "es_par.s", "w") as esf:
        for l in es_novl:
            esf.write(l + "\n")
    with open(out_dir_cr + "fr_par.s", "w") as frf:
        for l in fr_novl:
            frf.write(l + "\n")
    with open(out_dir_cr + "it_par.s", "w") as itf:
        for l in it_novl:
            itf.write(l + "\n")

    with open(out_dir_wr + "es_par.s", "w") as esf:
        for l in es_wr_novl:
            esf.write(l + "\n")
    with open(out_dir_wr + "fr_par.s", "w") as frf:
        for l in fr_wr_novl:
            frf.write(l + "\n")
    with open(out_dir_wr + "it_par.s", "w") as itf:
        for l in it_wr_novl:
            itf.write(l + "\n")

    with open(out_dir_cr + "es_speaker.csv", "w") as esspeakerf:
        for l in es_speaker_cr_novl:
            esspeakerf.write(l + "\n")
    with open(out_dir_cr + "fr_speaker.csv", "w") as frspeakerf:
        for l in fr_speaker_cr_novl:
            frspeakerf.write(l + "\n")
    with open(out_dir_cr + "it_speaker.csv", "w") as itspeakerf:
        for l in it_speaker_cr_novl:
            itspeakerf.write(l + "\n")
    with open(out_dir_wr + "es_speaker.csv", "w") as esspeakerf:
        for l in es_speaker_wr_novl:
            esspeakerf.write(l + "\n")
    with open(out_dir_wr + "fr_speaker.csv", "w") as frspeakerf:
        for l in fr_speaker_wr_novl:
            frspeakerf.write(l + "\n")
    with open(out_dir_wr + "it_speaker.csv", "w") as itspeakerf:
        for l in it_speaker_wr_novl:
            itspeakerf.write(l + "\n")
    
    with open(out_dir_cr + "es_category.csv", "w") as escategoryf:
        for l in es_category_cr_novl:
            escategoryf.write(l + "\n")
    with open(out_dir_cr + "fr_category.csv", "w") as frcategoryf:
        for l in fr_category_cr_novl:
            frcategoryf.write(l + "\n")
    with open(out_dir_cr + "it_category.csv", "w") as itcategoryf:
        for l in it_category_cr_novl:
            itcategoryf.write(l + "\n")
    with open(out_dir_wr + "es_category.csv", "w") as escategoryf:
        for l in es_category_wr_novl:
            escategoryf.write(l + "\n")
    with open(out_dir_wr + "fr_category.csv", "w") as frcategoryf:
        for l in fr_category_wr_novl:
            frcategoryf.write(l + "\n")
    with open(out_dir_wr + "it_category.csv", "w") as itcategoryf:
        for l in it_category_wr_novl:
            itcategoryf.write(l + "\n")

    with open(out_dir_cr + "es_gterms.csv", "w") as esgtermscrf:
        for l in es_add_gterms_cr_novl:
            esgtermscrf.write(l + "\n")
    with open(out_dir_cr + "it_gterms.csv", "w") as itgtermscrf:
        for l in it_add_gterms_cr_novl:
            itgtermscrf.write(l + "\n")
    with open(out_dir_cr + "fr_gterms.csv", "w") as frgtermscrf:
        for l in fr_add_gterms_cr_novl:
            frgtermscrf.write(l + "\n")
    with open(out_dir_wr + "es_gterms.csv", "w") as esgtermswrf:
        for l in es_add_gterms_wr_novl:
            esgtermswrf.write(l + "\n")
    with open(out_dir_wr + "it_gterms.csv", "w") as itgtermswrf:
        for l in it_add_gterms_wr_novl:
            itgtermswrf.write(l + "\n")
    with open(out_dir_wr + "fr_gterms.csv", "w") as frgtermswrf:
        for l in fr_add_gterms_wr_novl:
            frgtermswrf.write(l + "\n")

    print(f"Found {len(ovl)} duplicates.")
    print(f"Remaining {len(en_novl)} sentences.")
    print("Done.")


if __name__ == '__main__':
    args = sys.argv[1:]

    check_overlap(
        en_cs_mustc=args[0], 
        en_de_mustc=args[1], 
        en_es_mustc=args[2],  
        en_fr_mustc=args[3], 
        en_it_mustc=args[4], 
        en_nl_mustc=args[5],
        en_pt_mustc=args[6], 
        en_ro_mustc=args[7], 
        en_ru_mustc=args[8],
        
        en_par_mustshe=args[9],
        es_par_mustshe=args[10],
        fr_par_mustshe=args[11],
        it_par_mustshe=args[12],

        es_speaker_mustshe=args[13],
        es_category_mustshe=args[14],
        es_gterms_mustshe=args[15],
        fr_speaker_mustshe=args[16],
        fr_category_mustshe=args[17],
        fr_gterms_mustshe=args[18],
        it_speaker_mustshe=args[19],
        it_category_mustshe=args[20],
        it_gterms_mustshe=args[21],

        es_wr_par_mustshe=args[22],
        fr_wr_par_mustshe=args[23],
        it_wr_par_mustshe=args[24],

        es_wr_speaker_mustshe=args[25],
        es_wr_category_mustshe=args[26],
        es_wr_gterms_mustshe=args[27],
        fr_wr_speaker_mustshe=args[28],
        fr_wr_category_mustshe=args[29],
        fr_wr_gterms_mustshe=args[30],
        it_wr_speaker_mustshe=args[31],
        it_wr_category_mustshe=args[32],
        it_wr_gterms_mustshe=args[33],

        out_dir_cr=args[34],
        out_dir_wr=args[35]
    )
    