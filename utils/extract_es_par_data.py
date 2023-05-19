import sys
import tqdm

def create_language_pair_dict(en, tl):
    with open(en, "r") as ef:
        with open(tl, "r") as tf:
            en_lines = ef.read().splitlines()
            tl_lines = tf.read().splitlines()
            return dict(zip(en_lines, tl_lines))

def extract_parallel_sentences(en_es, es_en, en_cs, cs_en, en_de, de_en, en_fr, fr_en, en_it, it_en, en_nl, nl_en, en_pt, pt_en, en_ro, ro_en, en_ru, ru_en, out_dir):

    en_cs_d = create_language_pair_dict(en_cs, cs_en)
    en_de_d = create_language_pair_dict(en_de, de_en)
    en_es_d = create_language_pair_dict(en_es, es_en)
    en_fr_d = create_language_pair_dict(en_fr, fr_en)
    en_it_d = create_language_pair_dict(en_it, it_en)
    en_nl_d = create_language_pair_dict(en_nl, nl_en)
    en_pt_d = create_language_pair_dict(en_pt, pt_en)
    en_ro_d = create_language_pair_dict(en_ro, ro_en)
    en_ru_d = create_language_pair_dict(en_ru, ru_en)

    par_cs = {"tl": [], "es": []}
    par_de = {"tl": [], "es": []}
    par_fr = {"tl": [], "es": []}
    par_it = {"tl": [], "es": []}
    par_nl = {"tl": [], "es": []}
    par_pt = {"tl": [], "es": []}
    par_ro = {"tl": [], "es": []}
    par_ru = {"tl": [], "es": []}

    for en_l, es_l in tqdm.tqdm(en_es_d.items()):
        if en_l in en_cs_d:
            par_cs["tl"].append(en_cs_d[en_l])
            par_cs["es"].append(en_es_d[en_l])
        if en_l in en_de_d:
            par_de["tl"].append(en_de_d[en_l])
            par_de["es"].append(en_es_d[en_l])
        if en_l in en_fr_d:
            par_fr["tl"].append(en_fr_d[en_l])
            par_fr["es"].append(en_es_d[en_l])
        if en_l in en_it_d:
            par_it["tl"].append(en_it_d[en_l])
            par_it["es"].append(en_es_d[en_l])
        if en_l in en_nl_d:
            par_nl["tl"].append(en_nl_d[en_l])
            par_nl["es"].append(en_es_d[en_l])
        if en_l in en_pt_d:
            par_pt["tl"].append(en_pt_d[en_l])
            par_pt["es"].append(en_es_d[en_l])
        if en_l in en_ro_d:
            par_ro["tl"].append(en_ro_d[en_l])
            par_ro["es"].append(en_es_d[en_l])
        if en_l in en_ru_d:
            par_ru["tl"].append(en_ru_d[en_l])
            par_ru["es"].append(en_es_d[en_l])

 
    with open(out_dir + "cs-es.s", "w") as cs_f:
        with open(out_dir + "de-es.s", "w") as de_f:
                with open(out_dir + "fr-es.s", "w") as fr_f:
                    with open(out_dir + "it-es.s", "w") as it_f:
                        with open(out_dir + "nl-es.s", "w") as nl_f:
                            with open(out_dir + "pt-es.s", "w") as pt_f:
                                with open(out_dir + "ro-es.s", "w") as ro_f:
                                    with open(out_dir + "ru-es.s", "w") as ru_f:
                                            with open(out_dir + "es-cs.s", "w") as cs_f2:
                                                with open(out_dir + "es-de.s", "w") as de_f2:
                                                        with open(out_dir + "es-fr.s", "w") as fr_f2:
                                                            with open(out_dir + "es-it.s", "w") as it_f2:
                                                                with open(out_dir + "es-nl.s", "w") as nl_f2:
                                                                    with open(out_dir + "es-pt.s", "w") as pt_f2:
                                                                        with open(out_dir + "es-ro.s", "w") as ro_f2:
                                                                            with open(out_dir + "es-ru.s", "w") as ru_f2:
                                                                                for l, l2 in zip(par_cs["tl"], par_cs["es"]):
                                                                                    cs_f.write(l + "\n")
                                                                                    cs_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_de["tl"], par_de["es"]):
                                                                                    de_f.write(l + "\n")
                                                                                    de_f2.write(l2 + "\n")

                                                                                for l, l2 in zip(par_fr["tl"], par_fr["es"]):
                                                                                    fr_f.write(l + "\n")
                                                                                    fr_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_it["tl"], par_it["es"]):
                                                                                    it_f.write(l + "\n")
                                                                                    it_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_nl["tl"], par_nl["es"]):
                                                                                    nl_f.write(l + "\n")
                                                                                    nl_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_pt["tl"], par_pt["es"]):
                                                                                    pt_f.write(l + "\n")
                                                                                    pt_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_ro["tl"], par_ro["es"]):
                                                                                    ro_f.write(l + "\n")
                                                                                    ro_f2.write(l2 + "\n")
                                                                                for l, l2 in zip(par_ru["tl"], par_ru["es"]):
                                                                                    ru_f.write(l + "\n")
                                                                                    ru_f2.write(l2 + "\n")
                                                                                

    print("Done.")


if __name__ == '__main__':
    args = sys.argv[1:]

    extract_parallel_sentences(
        en_es=args[0],
        es_en=args[1],
        en_cs=args[2],
        cs_en=args[3],
        en_de=args[4],
        de_en=args[5],
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