import sys
import tqdm

def create_language_pair_dict(en, tl):
    with open(en, "r") as ef:
        with open(tl, "r") as tf:
            en_lines = ef.read().splitlines()
            tl_lines = tf.read().splitlines()
            return dict(zip(en_lines, tl_lines))

def check_overlap(en_cs_mustc, en_de_mustc, en_es_mustc, en_fr_mustc, en_it_mustc, en_nl_mustc, en_pt_mustc, en_ro_mustc, en_ru_mustc, 
    cs_mustc, de_mustc, es_mustc, fr_mustc, it_mustc, nl_mustc, pt_mustc, ro_mustc, ru_mustc, en_par_mustshe, out_dir):

    en_cs = create_language_pair_dict(en_cs_mustc, cs_mustc)
    en_de = create_language_pair_dict(en_de_mustc, de_mustc)
    en_es = create_language_pair_dict(en_es_mustc, es_mustc)
    en_fr = create_language_pair_dict(en_fr_mustc, fr_mustc)
    en_it = create_language_pair_dict(en_it_mustc, it_mustc)
    en_nl = create_language_pair_dict(en_nl_mustc, nl_mustc)
    en_pt = create_language_pair_dict(en_pt_mustc, pt_mustc)
    en_ro = create_language_pair_dict(en_ro_mustc, ro_mustc)
    en_ru = create_language_pair_dict(en_ru_mustc, ru_mustc)

    num_before = len(en_cs) + len(en_de) + len(en_es) + len(en_fr) + len(en_it) + len(en_nl) + len(en_pt) + len(en_ro) + len(en_ru)

    with open(en_par_mustshe, "r") as ef:
        en_mustshe = ef.read().splitlines()

    for l in tqdm.tqdm(en_mustshe):
        if l in en_cs.keys():
            del en_cs[l]
        if l in en_de.keys():
            del en_de[l]
        if l in en_es.keys():
            del en_es[l]
        if l in en_fr.keys():
            del en_fr[l]
        if l in en_it.keys():
            del en_it[l]
        if l in en_nl.keys():
            del en_nl[l]
        if l in en_pt.keys():
            del en_pt[l]
        if l in en_ro.keys():
            del en_ro[l]
        if l in en_ru.keys():
            del en_ru[l]
        
    num_after = len(en_cs) + len(en_de) + len(en_es) + len(en_fr) + len(en_it) + len(en_nl) + len(en_pt) + len(en_ro) + len(en_ru)
    print(f"Found {num_before - num_after} duplicates.")
    print(f"Remaining {num_after} sentences.")

    # cs
    with open(out_dir + "en-cs.s", "w") as sf:
        with open(out_dir + "cs-en.t", "w") as tf:
            for l in en_cs.keys():
                sf.write(l + "\n")
                tf.write(l + "\n")
    with open(out_dir + "cs-en.s", "w") as sf:
        with open(out_dir + "en-cs.t", "w") as tf:
            for l in en_cs.values():
                sf.write(l + "\n")
                tf.write(l + "\n")
    # de
    with open(out_dir + "en-de.s", "w") as sf:
        with open(out_dir + "de-en.t", "w") as tf:
            for l in en_de.keys():
                sf.write(l + "\n")
                tf.write(l + "\n")
    with open(out_dir + "de-en.s", "w") as sf:
        with open(out_dir + "en-de.t", "w") as tf:
            for l in en_de.values():
                sf.write(l + "\n")
                tf.write(l + "\n")
    # es
    with open(out_dir + "en-es.s", "w") as sf:
        with open(out_dir + "es-en.t", "w") as tf:
            for l in en_es.keys():
                sf.write(l + "\n")
                tf.write(l + "\n")
    with open(out_dir + "es-en.s", "w") as sf:
        with open(out_dir + "en-es.t", "w") as tf:
            for l in en_es.values():
                sf.write(l + "\n")
                tf.write(l + "\n")
    # fr
    with open(out_dir + "en-fr.s", "w") as sf:
        with open(out_dir + "fr-en.t", "w") as tf:
            for l in en_fr.keys():
                sf.write(l + "\n")
                tf.write(l + "\n")
    with open(out_dir + "fr-en.s", "w") as sf:
        with open(out_dir + "en-fr.t", "w") as tf:
            for l in en_fr.values():
                sf.write(l + "\n")
                tf.write(l + "\n")
    # it
    with open(out_dir + "en-it.s", "w") as sf:
        with open(out_dir + "it-en.t", "w") as tf:
            for l in en_it.keys():
                sf.write(l + "\n")
                tf.write(l + "\n")
    with open(out_dir + "it-en.s", "w") as sf:
        with open(out_dir + "en-it.t", "w") as tf:
            for l in en_it.values():
                sf.write(l + "\n")
                tf.write(l + "\n")
    # nl
    with open(out_dir + "en-nl.s", "w") as sf:
        with open(out_dir + "nl-en.t", "w") as tf:
            for l in en_nl.keys():
                sf.write(l + "\n")
                tf.write(l + "\n")
    with open(out_dir + "nl-en.s", "w") as sf:
        with open(out_dir + "en-nl.t", "w") as tf:
            for l in en_nl.values():
                sf.write(l + "\n")
                tf.write(l + "\n")
    # pt
    with open(out_dir + "en-pt.s", "w") as sf:
        with open(out_dir + "pt-en.t", "w") as tf:
            for l in en_pt.keys():
                sf.write(l + "\n")
                tf.write(l + "\n")
    with open(out_dir + "pt-en.s", "w") as sf:
        with open(out_dir + "en-pt.t", "w") as tf:
            for l in en_pt.values():
                sf.write(l + "\n")
                tf.write(l + "\n")
    # ro
    with open(out_dir + "en-ro.s", "w") as sf:
        with open(out_dir + "ro-en.t", "w") as tf:
            for l in en_ro.keys():
                sf.write(l + "\n")
                tf.write(l + "\n")
    with open(out_dir + "ro-en.s", "w") as sf:
        with open(out_dir + "en-ro.t", "w") as tf:
            for l in en_ro.values():
                sf.write(l + "\n")
                tf.write(l + "\n")
    # ru
    with open(out_dir + "en-ru.s", "w") as sf:
        with open(out_dir + "ru-en.t", "w") as tf:
            for l in en_ru.keys():
                sf.write(l + "\n")
                tf.write(l + "\n")
    with open(out_dir + "ru-en.s", "w") as sf:
        with open(out_dir + "en-ru.t", "w") as tf:
            for l in en_ru.values():
                sf.write(l + "\n")
                tf.write(l + "\n")

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
        cs_mustc=args[9], 
        de_mustc=args[10], 
        es_mustc=args[11],  
        fr_mustc=args[12], 
        it_mustc=args[13], 
        nl_mustc=args[14],
        pt_mustc=args[15], 
        ro_mustc=args[16], 
        ru_mustc=args[17],
        en_par_mustshe=args[18],
        out_dir=args[19]
    )
    