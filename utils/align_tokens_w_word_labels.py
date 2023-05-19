import argparse
from string import punctuation

parser = argparse.ArgumentParser(description='align_tokens_w_word_labels.py')
parser.add_argument('-text_path', required=True, default=None)
parser.add_argument('-label_path', required=True, default=None)
parser.add_argument('-out_path', required=True, default=None)

def main():

    opt = parser.parse_args()
    text_path = opt.text_path
    label_path = opt.label_path
    out_path = opt.out_path

    text_file = open(text_path, newline='', encoding='utf-8')
    label_file = open(label_path, newline='', encoding='utf-8')
    out_file = open(out_path, "w")

    punctuation_marks = [".", ",", "!", "?", ":", ";", "¿", "¡", "\"", "\n", "(", ")", "...", "-", "—", "«", "»"]
    tok_marks = ["@@", "&apos", "&#124", "&amp", "&lt", "&gt", "&quot;", "&#91", "&#93"]
                    
    tok_labels = []

    # stats
    num_neut = 0
    num_femi = 0
    num_masc = 0

    for text, labels in zip(text_file, label_file):
        word_labels = labels.split()
        word_idx = 0
        tok_labels_str = ""
        tokens = text.split()
        # print(len(tokens), len(word_labels))
        # print(text)
        # print(word_labels)
        quote = 0
        for i, tok in enumerate(tokens):
            # print(tok, word_idx)
            if tok in punctuation_marks and tok not in tok_marks:
                # print(tok)
                # add neuter gender label
                # print("--neuter: ", tok)
                tok_labels_str += '0'
                num_neut += 1
            else:
                # if tok == "&quot;" and tokens[i-1] == ".":
                    # print("........")
                if tok == "&quot;" and quote % 2 != 0:
                    tok_labels_str += word_labels[word_idx-1]
                    quote += 1
                else:
                    if word_idx == len(word_labels):
                        # print(tok, tokens[i-1]) 
                        word_idx -= 1 # TODO fix this
                    tok_labels_str += word_labels[word_idx]
                    if word_labels[word_idx] == "0":
                        num_neut += 1
                    elif word_labels[word_idx] == "1":
                        num_masc += 1
                    else:
                        num_femi += 1 
                    # print("word label: ", word_labels[word_idx])
                    interm_subword = False
                    for m in tok_marks:
                        if m in tok:
                            interm_subword = True
                            if tok == "&quot;":
                                quote += 1
                            break
                    if not interm_subword:
                        # print("interim: ", tok, tokens[i-1])
                        word_idx += 1
                        # print("niever: ", tok)
                    # else:
                    #     # subword and not last token of word
                    #     continue
                # print("i: ", i, len(tokens)-1)
            if i < len(tokens) - 1:
                # print("space")
                tok_labels_str += " "

        if len(tokens) != len(tok_labels_str.split()):
            print("Inconsistent lengths!")

        # print(tok_labels_str.split())
        tok_labels.append(tok_labels_str)
        out_file.write(tok_labels_str + '\n')
    print(max([len(lab) for lab in tok_labels]))

    print("# neuter:    ", num_neut)
    print("# masculine: ", num_masc)
    print("# feminine:  ", num_femi)

if __name__ == '__main__':
    main()