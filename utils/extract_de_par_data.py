import sys
import tqdm

def create_language_pair_dict(en, tl):
    with open(en, "r") as ef:
        with open(tl, "r") as tf:
            en_lines = ef.read().splitlines()
            tl_lines = tf.read().splitlines()
            return dict(zip(en_lines, tl_lines))

def extract_parallel_sentences(en_de, de_en, en_cs, cs_en, en_es, es_en, en_fr, fr_en, en_it, it_en, en_nl, nl_en, en_pt, pt_en, en_ro, ro_en, en_ru, ru_en, out_dir):

    en_cs_d = create_language_pair_dict(en_cs, cs_en)
    en_de_d = create_language_pair_dict(en_de, de_en)
    en_es_d = create_language_pair_dict(en_es, es_en)
    en_fr_d = create_language_pair_dict(en_fr, fr_en)
    en_it_d = create_language_pair_dict(en_it, it_en)
    en_nl_d = create_language_pair_dict(en_nl, nl_en)
    en_pt_d = create_language_pair_dict(en_pt, pt_en)
    en_ro_d = create_language_pair_dict(en_ro, ro_en)
    en_ru_d = create_language_pair_dict(en_ru, ru_en)

    par_cs = {"tl": [], "de": []}
    par_es = {"tl": [], "de": []}
    par_fr = {"tl": [], "de": []}
    par_it = {"tl": [], "de": []}
    par_nl = {"tl": [], "de": []}
    par_pt = {"tl": [], "de": []}
    par_ro = {"tl": [], "de": []}
    par_ru = {"tl": [], "de": []}

    for en_l, de_l in tqdm.tqdm(en_de_d.items()):
        if en_l in en_cs_d:
            par_cs["tl"].append(en_cs_d[en_l])
            par_cs["de"].append(en_de_d[en_l])
        if en_l in en_es_d:
            par_es["tl"].append(en_es_d[en_l])
            par_es["de"].append(en_de_d[en_l])
        if en_l in en_fr_d:
            par_fr["tl"].append(en_fr_d[en_l])
            par_fr["de"].append(en_de_d[en_l])
        if en_l in en_it_d:
            par_it["tl"].append(en_it_d[en_l])
            par_it["de"].append(en_de_d[en_l])
        if en_l in en_nl_d:
            par_nl["tl"].append(en_nl_d[en_l])
            par_nl["de"].append(en_de_d[en_l])
        if en_l in en_pt_d:
            par_pt["tl"].append(en_pt_d[en_l])
            par_pt["de"].append(en_de_d[en_l])
        if en_l in en_ro_d:
            par_ro["tl"].append(en_ro_d[en_l])
            par_ro["de"].append(en_de_d[en_l])
        if en_l in en_ru_d:
            par_ru["tl"].append(en_ru_d[en_l])
            par_ru["de"].append(en_de_d[en_l])

 
    with open(out_dir + "cs-de.s", "w") as cs_f:
        with open(out_dir + "es-de.s", "w") as es_f:
                with open(out_dir + "fr-de.s", "w") as fr_f:
                    with open(out_dir + "it-de.s", "w") as it_f:
                        with open(out_dir + "nl-de.s", "w") as nl_f:
                            with open(out_dir + "pt-de.s", "w") as pt_f:
                                with open(out_dir + "ro-de.s", "w") as ro_f:
                                    with open(out_dir + "ru-de.s", "w") as ru_f:
                                            with open(out_dir + "de-cs.s", "w") as cs_f2:
                                                with open(out_dir + "de-es.s", "w") as es_f2:
                                                        with open(out_dir + "de-fr.s", "w") as fr_f2:
                                                            with open(out_dir + "de-it.s", "w") as it_f2:
                                                                with open(out_dir + "de-nl.s", "w") as nl_f2:
                                                                    with open(out_dir + "de-pt.s", "w") as pt_f2:
                                                                        with open(out_dir + "de-ro.s", "w") as ro_f2:
                                                                            with open(out_dir + "de-ru.s", "w") as ru_f2:
                                                                                for l, l2 in zip(par_cs["tl"], par_cs["de"]):
                                                                                    cs_f.write(l + "\n")
                                                                                    cs_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_es["tl"], par_es["de"]):
                                                                                    es_f.write(l + "\n")
                                                                                    es_f2.write(l2 + "\n")

                                                                                for l, l2 in zip(par_fr["tl"], par_fr["de"]):
                                                                                    fr_f.write(l + "\n")
                                                                                    fr_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_it["tl"], par_it["de"]):
                                                                                    it_f.write(l + "\n")
                                                                                    it_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_nl["tl"], par_nl["de"]):
                                                                                    nl_f.write(l + "\n")
                                                                                    nl_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_pt["tl"], par_pt["de"]):
                                                                                    pt_f.write(l + "\n")
                                                                                    pt_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_ro["tl"], par_ro["de"]):
                                                                                    ro_f.write(l + "\n")
                                                                                    ro_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_ru["tl"], par_ru["de"]):
                                                                                    ru_f.write(l + "\n")
                                                                                    ru_f2.write(l2 + "\n")
                                                                                

    print("Done.")


if __name__ == '__main__':
    args = sys.argv[1:]

    extract_parallel_sentences(
        en_de=args[0],
        de_en=args[1],
        en_cs=args[2],
        cs_en=args[3],
        en_es=args[4],
        es_en=args[5],
        en_fr=args[6],
        fr_en=args[7],
        en_it=args[8],
        it_en=args[9],
        en_nl=args[10],
        nl_en=args[11],
        en_pt=args[12],
        pt_en=args[13],
        en_ro=args[14],
        ro_en=args[15],
        en_ru=args[16],
        ru_en=args[17],
        out_dir=args[18]
    )