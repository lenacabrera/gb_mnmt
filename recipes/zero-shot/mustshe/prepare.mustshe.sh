#!/bin/bash
source ./recipes/zero-shot/config.sh

REMOVE_OVERLAP_W_MUSTC=$1

mkdir -p $DATADIR/mustshe/raw
mkdir -p $DATADIR/mustshe/raw/correct_ref
mkdir -p $DATADIR/mustshe/raw/wrong_ref

# TODO add mode to args
python3 -u $NMTDIR/utils/prepro_tsv_mustshe.py $DATADIR/mustshe/raw/ correct_ref wrong_ref

if [[ $REMOVE_OVERLAP_W_MUSTC == true ]]; then
    echo "Remove sentences overlaping with MuST-C data"
    bash $SCRIPTDIR/mustshe/remove.overlap.mustc.mustshe.sh
fi

for ref in correct_ref wrong_ref; do
    for f in $DATADIR/mustshe/raw/$ref/*\_par.s; do
        lan="$(basename "$f")"
        sl=${lan:0:2}
        for tl in en es fr it; do
            if [ "$sl" != "$tl" ]; then
                cp $f $DATADIR/mustshe/raw/$ref/$sl-$tl.s
            fi
        done
        rm $f
    done
    for f in $DATADIR/mustshe/raw/$ref/*\.s; do
        lan="$(basename "$f")"
        sl=${lan:0:2}
        tl=${lan:3:2}
        cp $f $DATADIR/mustshe/raw/$ref/$tl-$sl.t
    done
done

rm $DATADIR/mustshe/raw/es_add.csv
rm $DATADIR/mustshe/raw/it_add.csv
rm $DATADIR/mustshe/raw/fr_add.csv

mkdir -p $DATADIR/mustshe/raw/correct_ref/all
mkdir -p $DATADIR/mustshe/raw/correct_ref/feminine
mkdir -p $DATADIR/mustshe/raw/correct_ref/masculine

mkdir -p $DATADIR/mustshe/raw/correct_ref/all/annotation
mkdir -p $DATADIR/mustshe/raw/correct_ref/feminine/annotation
mkdir -p $DATADIR/mustshe/raw/correct_ref/masculine/annotation

mkdir -p $DATADIR/mustshe/raw/wrong_ref/all
mkdir -p $DATADIR/mustshe/raw/wrong_ref/feminine
mkdir -p $DATADIR/mustshe/raw/wrong_ref/masculine

mkdir -p $DATADIR/mustshe/raw/wrong_ref/all/annotation
mkdir -p $DATADIR/mustshe/raw/wrong_ref/feminine/annotation
mkdir -p $DATADIR/mustshe/raw/wrong_ref/masculine/annotation

python3 -u $NMTDIR/utils/create_separate_gender_files_mustshe.py \
    	-raw_path $DATADIR/mustshe/raw \
        -json_path $NMTDIR/../output/

# for ref in correct_ref wrong_ref; do
#     for f in $DATADIR/mustshe/raw/$ref/*\.s; do
#         mv $f $DATADIR/mustshe/raw/$ref/all
#     done
#     for f in $DATADIR/mustshe/raw/$ref/*\.t; do
#         mv $f $DATADIR/mustshe/raw/$ref/all
#     done
#     for f in $DATADIR/mustshe/raw/$ref/*\.csv; do
#         mv $f $DATADIR/mustshe/raw/$ref/all/annotation
#     done
# done

# equal feminine, masculine instances
for ref in correct_ref wrong_ref; do
    for f in $DATADIR/mustshe/raw/$ref/*\.s; do
        rm $f 
    done
    for f in $DATADIR/mustshe/raw/$ref/*\.t; do
        rm $f
    done
    for f in $DATADIR/mustshe/raw/$ref/*\.csv; do
        rm $f
    done
done


# #  -> correct inconsistent mustshe instances
# python3 -u $NMTDIR/utils/correct_inconsistent_mustshe_instances.py \
#     -raw_path $DATADIR/mustshe/raw