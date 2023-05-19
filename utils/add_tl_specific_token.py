import os
import sys
import shutil


def prepend_tokens_iwslt(PREPRO_DIR):
    TLAN = ["it", "nl", "ro"]
    extended_TLAN = TLAN[:]
    extended_TLAN.append("en")
    print(extended_TLAN)

    if not os.path.exists(PREPRO_DIR + "/bos/"):
        os.mkdir(PREPRO_DIR + "/bos/")

    for set in ["train", "valid", "test"]:
        path = PREPRO_DIR + set + "/"
        path_bos = PREPRO_DIR + "/bos/" + set + "/"

        if not os.path.exists(path_bos):
            os.mkdir(path_bos)

        for tl in TLAN:
            print(tl)

            if set != "test":
                # target files
                file = "en-" + tl + ".t"
                with open(path + file) as fp:
                    lines = fp.read().splitlines()
                with open(path_bos + file, "w") as fp:
                    for line in lines:
                        # add target-language specific bos token
                        fp.write("#" + tl.upper() + " " + line + "\n")

                file = tl + "-en" + ".t"
                with open(path + file) as fp:
                    lines = fp.read().splitlines()
                with open(path_bos + file, "w") as fp:
                    for line in lines:
                        # add target-language specific bos token
                        fp.write("#" + 'en'.upper() + " " + line + "\n")

                # source files
                file = "en-" + tl + ".s"
                with open(path_bos + file, "w") as fp:
                    for line in lines:
                        fp.write(line + "\n")

                file = tl + "-en" + ".s"
                with open(path_bos + file, "w") as fp:
                    for line in lines:
                        fp.write(line + "\n")

            elif set == "test":
                for sl in extended_TLAN:
                    if sl != tl:
                        # source files
                        file = sl + "-" + tl + ".s"
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

                        file = tl + "-" + sl + ".s"
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

def prepend_tokens_mustc_twoway(PREPRO_DIR):
    TLAN = ["cs", "de", "en", "es", "fr", "it", "nl", "pt", "ro", "ru"]

    if not os.path.exists(PREPRO_DIR + "/no_bos/"):
        # destination for orig. data without bos token
        os.mkdir(PREPRO_DIR + "/no_bos/")
    if not os.path.exists(PREPRO_DIR + "/bos/"):
        # temporary directory for data with bos token
        os.mkdir(PREPRO_DIR + "/bos/")

    for set in ["train", "valid", "test"]:
        path = PREPRO_DIR + set + "/"
        path_bos = PREPRO_DIR + "/bos/" + set + "/"

        if not os.path.exists(path_bos):
            os.mkdir(path_bos)

        for sl in TLAN:
            for tl in TLAN:
                if sl != tl and (sl == "en" or tl == "en"):
                    if set in ["train", "valid"]:
                        # target files: add bos token for train and valid data
                        file = sl + "-" + tl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + tl.upper() + " " + line + "\n")

                        file = tl + "-" + sl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + sl.upper() + " " + line + "\n")

                    if set in ["train", "valid", "test"]:
                        # source files: keep as is for all sets
                        file = sl + "-" + tl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

                        file = tl + "-" + sl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

    shutil.move(PREPRO_DIR + "/train", PREPRO_DIR + "/no_bos/train")   
    shutil.move(PREPRO_DIR + "/valid", PREPRO_DIR + "/no_bos/valid")   
    shutil.move(PREPRO_DIR + "/test", PREPRO_DIR + "/no_bos/test")  

    shutil.move(PREPRO_DIR + "bos/train", PREPRO_DIR + "/train")   
    shutil.move(PREPRO_DIR + "bos/valid", PREPRO_DIR + "/valid")   
    shutil.move(PREPRO_DIR + "bos/test", PREPRO_DIR + "/test")   

    os.rmdir(PREPRO_DIR + "/bos")

def prepend_tokens_mustc_twowayES(PREPRO_DIR):
    TLAN = ["cs", "de", "en", "es", "fr", "it", "nl", "pt", "ro", "ru"]

    if not os.path.exists(PREPRO_DIR + "/no_bos/"):
        # destination for orig. data without bos token
        os.mkdir(PREPRO_DIR + "/no_bos/")
    if not os.path.exists(PREPRO_DIR + "/bos/"):
        # temporary directory for data with bos token
        os.mkdir(PREPRO_DIR + "/bos/")

    for set in ["train", "valid", "test"]:
        path = PREPRO_DIR + set + "/"
        path_bos = PREPRO_DIR + "/bos/" + set + "/"

        if not os.path.exists(path_bos):
            os.mkdir(path_bos)

        for sl in TLAN:
            for tl in TLAN:
                if sl != tl and (sl == "es" or tl == "es"):
                    if set in ["train", "valid"]:
                        # target files: add bos token for train and valid data
                        file = sl + "-" + tl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + tl.upper() + " " + line + "\n")

                        file = tl + "-" + sl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + sl.upper() + " " + line + "\n")

                    if set in ["train", "valid", "test"]:
                        # source files: keep as is for all sets
                        file = sl + "-" + tl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

                        file = tl + "-" + sl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

    shutil.move(PREPRO_DIR + "/train", PREPRO_DIR + "/no_bos/train")   
    shutil.move(PREPRO_DIR + "/valid", PREPRO_DIR + "/no_bos/valid")   
    shutil.move(PREPRO_DIR + "/test", PREPRO_DIR + "/no_bos/test")  

    shutil.move(PREPRO_DIR + "bos/train", PREPRO_DIR + "/train")   
    shutil.move(PREPRO_DIR + "bos/valid", PREPRO_DIR + "/valid")   
    shutil.move(PREPRO_DIR + "bos/test", PREPRO_DIR + "/test")   

    os.rmdir(PREPRO_DIR + "/bos")

def prepend_tokens_mustc_twowayDE(PREPRO_DIR):
    TLAN = ["cs", "de", "en", "es", "fr", "it", "nl", "pt", "ro", "ru"]

    if not os.path.exists(PREPRO_DIR + "/no_bos/"):
        # destination for orig. data without bos token
        os.mkdir(PREPRO_DIR + "/no_bos/")
    if not os.path.exists(PREPRO_DIR + "/bos/"):
        # temporary directory for data with bos token
        os.mkdir(PREPRO_DIR + "/bos/")

    for set in ["train", "valid", "test"]:
        path = PREPRO_DIR + set + "/"
        path_bos = PREPRO_DIR + "/bos/" + set + "/"

        if not os.path.exists(path_bos):
            os.mkdir(path_bos)

        for sl in TLAN:
            for tl in TLAN:
                if sl != tl and (sl == "de" or tl == "de"):
                    if set in ["train", "valid"]:
                        # target files: add bos token for train and valid data
                        file = sl + "-" + tl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + tl.upper() + " " + line + "\n")

                        file = tl + "-" + sl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + sl.upper() + " " + line + "\n")

                    if set in ["train", "valid"]:
                        # source files: keep as is for all sets
                        file = sl + "-" + tl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

                        file = tl + "-" + sl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

    shutil.move(PREPRO_DIR + "/train", PREPRO_DIR + "/no_bos/train")   
    shutil.move(PREPRO_DIR + "/valid", PREPRO_DIR + "/no_bos/valid")   
    # shutil.move(PREPRO_DIR + "/test", PREPRO_DIR + "/no_bos/test")  

    shutil.move(PREPRO_DIR + "bos/train", PREPRO_DIR + "/train")   
    shutil.move(PREPRO_DIR + "bos/valid", PREPRO_DIR + "/valid")   
    # shutil.move(PREPRO_DIR + "bos/test", PREPRO_DIR + "/test")   

    os.rmdir(PREPRO_DIR + "/bos")

def prepend_tokens_mustc_multiway(PREPRO_DIR):
    TLAN = ["cs", "de", "en", "es", "fr", "it", "nl", "pt", "ro", "ru"]

    if not os.path.exists(PREPRO_DIR + "/no_bos/"):
        # destination for orig. data without bos token
        os.mkdir(PREPRO_DIR + "/no_bos/")
    if not os.path.exists(PREPRO_DIR + "/bos/"):
        # temporary directory for data with bos token
        os.mkdir(PREPRO_DIR + "/bos/")

    for set in ["train", "valid", "test"]:
        path = PREPRO_DIR + set + "/"
        path_bos = PREPRO_DIR + "/bos/" + set + "/"

        if not os.path.exists(path_bos):
            os.mkdir(path_bos)

        for sl in TLAN:
            for tl in TLAN:
                if sl != tl:
                    if set in ["train", "valid"]:
                        # target files: add bos token for train and valid data
                        file = sl + "-" + tl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + tl.upper() + " " + line + "\n")

                        file = tl + "-" + sl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + sl.upper() + " " + line + "\n")

                    if set in ["train", "valid", "test"]:
                        # source files: keep as is for all sets
                        file = sl + "-" + tl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

                        file = tl + "-" + sl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

    shutil.move(PREPRO_DIR + "/train", PREPRO_DIR + "/no_bos/train")   
    shutil.move(PREPRO_DIR + "/valid", PREPRO_DIR + "/no_bos/valid")   
    shutil.move(PREPRO_DIR + "/test", PREPRO_DIR + "/no_bos/test")  

    shutil.move(PREPRO_DIR + "bos/train", PREPRO_DIR + "/train")   
    shutil.move(PREPRO_DIR + "bos/valid", PREPRO_DIR + "/valid")   
    shutil.move(PREPRO_DIR + "bos/test", PREPRO_DIR + "/test")   

    os.rmdir(PREPRO_DIR + "/bos")

def prepend_tokens_mustc_multiwayES(PREPRO_DIR):
    TLAN = ["cs", "de", "en", "es", "fr", "it", "nl", "pt", "ro", "ru"]

    if not os.path.exists(PREPRO_DIR + "/no_bos/"):
        # destination for orig. data without bos token
        os.mkdir(PREPRO_DIR + "no_bos/")
    if not os.path.exists(PREPRO_DIR + "bos/"):
        # temporary directory for data with bos token
        os.mkdir(PREPRO_DIR + "bos/")

    for set in ["train", "valid", "test"]:
        path = PREPRO_DIR + set + "/"
        path_bos = PREPRO_DIR + "bos/" + set + "/"

        if not os.path.exists(path_bos):
            os.mkdir(path_bos)

        for sl in TLAN:
            for tl in TLAN:
                if sl != tl and (sl == "es" or tl == "es"):
                    if set in ["train", "valid"]:
                        # target files: add bos token for train and valid data
                        file = sl + "-" + tl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + tl.upper() + " " + line + "\n")

                        file = tl + "-" + sl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + sl.upper() + " " + line + "\n")

                    if set in ["train", "valid"]:
                        # source files: keep as is for all sets
                        file = sl + "-" + tl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

                        file = tl + "-" + sl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

    shutil.move(PREPRO_DIR + "train", PREPRO_DIR + "no_bos/train")   
    shutil.move(PREPRO_DIR + "valid", PREPRO_DIR + "no_bos/valid")   
    # shutil.move(PREPRO_DIR + "/test", PREPRO_DIR + "/no_bos/test")  

    shutil.move(PREPRO_DIR + "bos/train", PREPRO_DIR + "train")   
    shutil.move(PREPRO_DIR + "bos/valid", PREPRO_DIR + "valid")   
    # shutil.move(PREPRO_DIR + "bos/test", PREPRO_DIR + "/test")   

    os.rmdir(PREPRO_DIR + "bos")


def prepend_tokens_mustc_multiwayEN(PREPRO_DIR):
    TLAN = ["cs", "de", "en", "es", "fr", "it", "nl", "pt", "ro", "ru"]

    if not os.path.exists(PREPRO_DIR + "/no_bos/"):
        # destination for orig. data without bos token
        os.mkdir(PREPRO_DIR + "/no_bos/")
    if not os.path.exists(PREPRO_DIR + "/bos/"):
        # temporary directory for data with bos token
        os.mkdir(PREPRO_DIR + "/bos/")

    for set in ["train", "valid", "test"]:
        path = PREPRO_DIR + set + "/"
        path_bos = PREPRO_DIR + "/bos/" + set + "/"

        if not os.path.exists(path_bos):
            os.mkdir(path_bos)

        for sl in TLAN:
            for tl in TLAN:
                if sl != tl and (sl == "en" or tl == "en"):
                    if set in ["train", "valid"]:
                        # target files: add bos token for train and valid data
                        file = sl + "-" + tl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + tl.upper() + " " + line + "\n")

                        file = tl + "-" + sl + ".t"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                # add target-language specific bos token
                                fp.write("#" + sl.upper() + " " + line + "\n")

                    if set in ["train", "valid", "test"]:
                        # source files: keep as is for all sets
                        file = sl + "-" + tl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

                        file = tl + "-" + sl + ".s"
                        print(file)
                        with open(path + file) as fp:
                            lines = fp.read().splitlines()
                        with open(path_bos + file, "w") as fp:
                            for line in lines:
                                fp.write(line + "\n")

    shutil.move(PREPRO_DIR + "/train", PREPRO_DIR + "/no_bos/train")   
    shutil.move(PREPRO_DIR + "/valid", PREPRO_DIR + "/no_bos/valid")   
    shutil.move(PREPRO_DIR + "/test", PREPRO_DIR + "/no_bos/test")  

    shutil.move(PREPRO_DIR + "bos/train", PREPRO_DIR + "/train")   
    shutil.move(PREPRO_DIR + "bos/valid", PREPRO_DIR + "/valid")   
    shutil.move(PREPRO_DIR + "bos/test", PREPRO_DIR + "/test")   

    os.rmdir(PREPRO_DIR + "/bos")



if __name__ == '__main__':
    args = sys.argv[1:]
    prepro_dir = args[0]
    input = args[1]
    if "iwslt" == input:
        prepend_tokens_iwslt(prepro_dir)
    elif "mustc_multiway" == input:
        prepend_tokens_mustc_multiway(prepro_dir)
    elif "mustc_multiwayES" == input:
        prepend_tokens_mustc_multiwayES(prepro_dir)
    elif "mustc_multiwayEN" == input:
        prepend_tokens_mustc_multiwayEN(prepro_dir)
    elif "mustc_twoway" == input:
        prepend_tokens_mustc_twoway(prepro_dir)
    elif "mustc_twowayES" == input:
        prepend_tokens_mustc_twowayES(prepro_dir)
    elif "mustc_twowayDE" == input:
        prepend_tokens_mustc_twowayDE(prepro_dir)
    else:
        "no target languages found... check prepro dir (argv[1][0])"
  