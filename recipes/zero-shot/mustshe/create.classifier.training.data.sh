
mkdir -p $DATADIR/mustshe/raw/train
mkdir -p $DATADIR/mustshe/raw/train/all
mkdir -p $DATADIR/mustshe/raw/train/all/gen_label
mkdir -p $DATADIR/mustshe/raw/train/all/gen_label/sent
mkdir -p $DATADIR/mustshe/raw/train/all/gen_label/word
mkdir -p $DATADIR/mustshe/raw/train/all/gen_label/tok
mkdir -p $DATADIR/mustshe/raw/train/feminine
mkdir -p $DATADIR/mustshe/raw/train/feminine/gen_label
mkdir -p $DATADIR/mustshe/raw/train/feminine/gen_label/sent
mkdir -p $DATADIR/mustshe/raw/train/feminine/gen_label/word
mkdir -p $DATADIR/mustshe/raw/train/feminine/gen_label/tok
mkdir -p $DATADIR/mustshe/raw/train/masculine
mkdir -p $DATADIR/mustshe/raw/train/masculine/gen_label
mkdir -p $DATADIR/mustshe/raw/train/masculine/gen_label/sent
mkdir -p $DATADIR/mustshe/raw/train/masculine/gen_label/word
mkdir -p $DATADIR/mustshe/raw/train/masculine/gen_label/tok

mkdir -p $DATADIR/mustshe/raw/valid/all
mkdir -p $DATADIR/mustshe/raw/valid/all/gen_label
mkdir -p $DATADIR/mustshe/raw/valid/all/gen_label/sent
mkdir -p $DATADIR/mustshe/raw/valid/all/gen_label/word
mkdir -p $DATADIR/mustshe/raw/valid/all/gen_label/tok
mkdir -p $DATADIR/mustshe/raw/valid/feminine
mkdir -p $DATADIR/mustshe/raw/valid/feminine/gen_label
mkdir -p $DATADIR/mustshe/raw/valid/feminine/gen_label/sent
mkdir -p $DATADIR/mustshe/raw/valid/feminine/gen_label/word
mkdir -p $DATADIR/mustshe/raw/valid/feminine/gen_label/tok
mkdir -p $DATADIR/mustshe/raw/valid/masculine
mkdir -p $DATADIR/mustshe/raw/valid/masculine/gen_label
mkdir -p $DATADIR/mustshe/raw/valid/masculine/gen_label/sent
mkdir -p $DATADIR/mustshe/raw/valid/masculine/gen_label/word
mkdir -p $DATADIR/mustshe/raw/valid/masculine/gen_label/tok

python3 -u $NMTDIR/utils/extract_all_mustshe_instances.py \
        -data_dir_path $DATADIR/mustshe/raw/

for set in train valid; do
    for gender_set in all; do
        for f in $DATADIR/mustshe/raw/$set/$gender_set/*.s; do
            lan="$(basename "$f")"
            sl=${lan:0:2} 
            tl=${lan:3:2} 
            cp $f $DATADIR/mustshe/raw/$set/$gender_set/$tl-$sl.t
            # for tl2 in en es fr it; do
            #     if [[ "$sl" != "$tl" ]] && [[ "$tl" != "$tl2" ]]; then
            #         cp $f $DATADIR/mustshe/raw/$set/$gender_set/$sl-$tl2.s
            #         cp $f $DATADIR/mustshe/raw/$set/$gender_set/$tl2-$sl.t
            #     fi
            # done
        done
    done
    rm -r $DATADIR/mustshe/raw/$set/feminine
    rm -r $DATADIR/mustshe/raw/$set/masculine
done
