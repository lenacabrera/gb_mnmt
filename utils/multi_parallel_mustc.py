import sys

def create_language_pair_dict(en, tl):
    with open(en, "r") as ef:
        with open(tl, "r") as tf:
            en_lines = ef.read().splitlines()
            tl_lines = tf.read().splitlines()
            return dict(zip(en_lines, tl_lines))

def extract_parallel_sentences(en_cs_path, en_de_path, en_es_path, en_fr_path, en_it_path, en_nl_path, en_pt_path, en_ro_path, en_ru_path, 
    cs_path, de_path, es_path, fr_path, it_path, nl_path, pt_path, ro_path, ru_path, out_dir):

    en_cs_d = create_language_pair_dict(en_cs_path, cs_path)
    en_de_d = create_language_pair_dict(en_de_path, de_path)
    en_es_d = create_language_pair_dict(en_es_path, es_path)
    en_fr_d = create_language_pair_dict(en_fr_path, fr_path)
    en_it_d = create_language_pair_dict(en_it_path, it_path)
    en_nl_d = create_language_pair_dict(en_nl_path, nl_path)
    en_pt_d = create_language_pair_dict(en_pt_path, pt_path)
    en_ro_d = create_language_pair_dict(en_ro_path, ro_path)
    en_ru_d = create_language_pair_dict(en_ru_path, ru_path)

    par = dict()

    for en_l in en_cs_d.keys():
        if en_l in en_de_d and en_l in en_es_d and en_l in en_fr_d and en_l in en_it_d and en_l in en_nl_d and en_l in en_pt_d and en_l in en_ro_d and en_l in en_ru_d:
            par[en_l] = {
                "cs": en_cs_d[en_l],
                "de": en_de_d[en_l],
                "es": en_es_d[en_l],
                "fr": en_fr_d[en_l],
                "it": en_it_d[en_l],
                "nl": en_nl_d[en_l],
                "pt": en_pt_d[en_l],
                "ro": en_ro_d[en_l],
                "ru": en_ru_d[en_l],
            }

    print(f"{len(par)} remaining sentences.")
    with open(out_dir + "en.s", "w") as en_f:
        with open(out_dir + "cs.s", "w") as cs_f:
            with open(out_dir + "de.s", "w") as de_f:
                with open(out_dir + "es.s", "w") as es_f:
                    with open(out_dir + "fr.s", "w") as fr_f:
                        with open(out_dir + "it.s", "w") as it_f:
                            with open(out_dir + "nl.s", "w") as nl_f:
                                with open(out_dir + "pt.s", "w") as pt_f:
                                    with open(out_dir + "ro.s", "w") as ro_f:
                                        with open(out_dir + "ru.s", "w") as ru_f:
                                            for en in par.keys():
                                                en_f.write(en + "\n")
                                                cs_f.write(par[en]["cs"] + "\n")
                                                de_f.write(par[en]["de"] + "\n")
                                                es_f.write(par[en]["es"] + "\n")
                                                fr_f.write(par[en]["fr"] + "\n")
                                                it_f.write(par[en]["it"] + "\n")
                                                nl_f.write(par[en]["nl"] + "\n")
                                                pt_f.write(par[en]["pt"] + "\n")
                                                ro_f.write(par[en]["ro"] + "\n")
                                                ru_f.write(par[en]["ru"] + "\n")
    print("Done.")


if __name__ == '__main__':
    args = sys.argv[1:]

    extract_parallel_sentences(
        en_cs_path=args[0], 
        en_de_path=args[1], 
        en_es_path=args[2],  
        en_fr_path=args[3], 
        en_it_path=args[4], 
        en_nl_path=args[5],
        en_pt_path=args[6], 
        en_ro_path=args[7], 
        en_ru_path=args[8],
        cs_path=args[9],
        de_path=args[10],
        es_path=args[11],
        fr_path=args[12],
        it_path=args[13],
        nl_path=args[14],
        pt_path=args[15],
        ro_path=args[16],
        ru_path=args[17],
        out_dir=args[18]
    )
