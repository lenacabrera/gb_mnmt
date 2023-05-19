import numpy as np
import json
import sys
import argparse

parser = argparse.ArgumentParser(description='eval_gender_accuracy.py')

parser.add_argument('-pred_path', required=True, default=None)
parser.add_argument('-gterms_path', required=True)
parser.add_argument('-speaker_path', required=True)
parser.add_argument('-category_path', required=True)
parser.add_argument('-stats_path', required=True)


def main():

    opt = parser.parse_args()
    pred_path = opt.pred_path
    gterms_path = opt.gterms_path
    speaker_path = opt.speaker_path
    category_path = opt.category_path
    stats_path = opt.stats_path

    pred_file = open(pred_path, "r", encoding="utf-8")
    gterms_file = open(gterms_path, "r", encoding="utf-8")
    speaker_file = open(speaker_path, "r", encoding="utf-8")
    category_file = open(category_path, "r", encoding="utf-8")

    accuracies_f = []
    accuracies_m = []

    accuracies_1F = []
    accuracies_2F = []
    accuracies_1M = []
    accuracies_2M = []

    for pred, gterms, speaker, category in zip(pred_file, gterms_file, speaker_file, category_file):
        pred_gterms = []
        gterms_list = [t for t in gterms.split(" ") if (t != '' and t != '\n')]

        for gterm in gterms_list:
            if gterm in pred:
                pred_gterms.append(gterm)
        # speaker gender
        acc = len(pred_gterms) / len(gterms_list)
        if speaker.replace("\n", "").lower() == "she":
            accuracies_f.append(acc)
        if speaker.replace("\n", "").lower() == "he":
            accuracies_m.append(acc)
        # gender of referred entity
        if category.replace("\n", "") == "1F":
            accuracies_1F.append(acc)
        if category.replace("\n", "") == "2F":
            accuracies_2F.append(acc)
        if category.replace("\n", "") == "1M":
            accuracies_1M.append(acc)
        if category.replace("\n", "") == "2M":
            accuracies_2M.append(acc)

    num_f = len(accuracies_f)
    num_m = len(accuracies_m)
    num_all = num_f + num_m

    num_1F = len(accuracies_1F)
    num_2F = len(accuracies_2F)
    num_1M = len(accuracies_1M)
    num_2M = len(accuracies_2M)

    avg_acc_f = np.average(np.array(accuracies_f))
    avg_acc_m = np.average(np.array(accuracies_m))
    avg_acc = np.average(np.array(accuracies_f + accuracies_m))

    avg_acc_1F = np.average(np.array(accuracies_1F))
    avg_acc_2F = np.average(np.array(accuracies_2F))
    avg_acc_1M = np.average(np.array(accuracies_1M))
    avg_acc_2M = np.average(np.array(accuracies_2M))
    avg_acc_cat = np.average(np.array(accuracies_1F + accuracies_2F + accuracies_1M + accuracies_2M))

    # print(f"# female: {num_f}, accuracy: {round(avg_acc_f * 100, 1)}")
    # print(f"# male  : {num_m}, accuracy: {round(avg_acc_m * 100, 1)}")
    # print(f"# total : {num_all}, accuracy: {round(avg_acc * 100, 1)}")

    stats = {
        "num_f": num_f,
        "num_m": num_m,
        "num_all": num_all,
        "avg_acc_f": round(avg_acc_f * 100, 1),
        "avg_acc_m": round(avg_acc_m * 100, 1),
        "avg__acc": round(avg_acc * 100, 1),

        "num_1F": num_1F,
        "num_2F": num_2F,
        "num_1M": num_1M,
        "num_2M": num_2M,
        "avg_acc_cat": round(avg_acc_cat * 100, 1),
        "avg_acc_1F": round(avg_acc_1F * 100, 1),
        "avg_acc_2F": round(avg_acc_2F * 100, 1),
        "avg_acc_1M": round(avg_acc_1M * 100, 1),
        "avg_acc_2M": round(avg_acc_2M * 100, 1)
    }

    with open(stats_path, "w") as outfile:
        json.dump(stats, outfile, indent=2)


if __name__ == "__main__":
    # args = sys.argv

    # eval_gender_acc(
    #     pred_path=args[0],
    #     gterms_path=args[1],
    #     speaker_path=args[2],
    #     stats_path=args[3]
    # )
    main()
