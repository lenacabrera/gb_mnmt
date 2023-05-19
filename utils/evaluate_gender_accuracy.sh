#!/bin/bash

MODEL=transformer.mustc
TRAIN_SET=twoway.r32.q
PIVOT=en

# direct
for ref in correct_ref wrong_ref; do
    DIRPATH=$OUTDIR/$MODEL/mustshe/$TRAIN_SET/$ref
    for sl in en es it fr; do
        for tl in es it fr; do
            if [ "$sl" != "$tl" ]; then
                python3 -u $NMTDIR/utils/eval_gender_accuracy.py \
                        -pred_path $DIRPATH/$sl-$tl.pred.pt \
                        -gterms_path $DATADIR/mustshe/raw/$ref/add_info/${tl}_gterms.csv \
                        -speaker_path $DATADIR/mustshe/raw/$ref/add_info/${tl}_speaker.csv \
                        -category_path $DATADIR/mustshe/raw/$ref/add_info/${tl}_category.csv \
                        -stats_path $OUTDIR/$MODEL/mustshe/$TRAIN_SET/$ref/$sl-$tl.stats.json
            fi
        done
    done
    out=/home/lperez/output/results_gender_acc_${TRAIN_SET}_${ref}.csv
    rm -f $out
    echo "set;avg_acc;avg_acc_f;avg_acc_m;avg_acc_cat;avg_acc_1F;avg_acc_2F;avg_acc_1M;avg_acc_2M;num_f;num_m;num_1F;num_2F;num_1M;num_2M" >> $out
    for f in $DIRPATH/*\.json; do
        filename="$(basename "$f")"
        [[ ${filename} =~ [a-z][a-z]-[a-z][a-z] ]] && set=$BASH_REMATCH
        while read -r line; do 
            if [[ $line == "\"avg__acc"* ]]; then
                [[ ${line:12:4} =~ ^.[0-9]*.[0-9]* ]] && avg_acc=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_f"* ]]; then
                [[ ${line:13:4} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_f=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_m"* ]]; then
                [[ ${line:13:4} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_m=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_cat"* ]]; then
                [[ ${line:15:4} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_cat=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_1F"* ]]; then
                [[ ${line:14:5} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_1F=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_2F"* ]]; then
                [[ ${line:14:5} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_2F=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_1M"* ]]; then
                [[ ${line:14:5} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_1M=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_2M"* ]]; then
                [[ ${line:14:5} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_2M=$BASH_REMATCH
            fi

            if [[ $line == "\"num_f"* ]]; then
                [[ ${line:9:4} =~ ^.[0-9]* ]] && num_f=$BASH_REMATCH
            fi
            if [[ $line == "\"num_m"* ]]; then
                [[ ${line:9:4} =~ ^.[0-9]* ]] && num_m=$BASH_REMATCH
            fi
            if [[ $line == "\"num_1F"* ]]; then
                [[ ${line:10:4} =~ ^.[0-9]* ]] && num_1F=$BASH_REMATCH
            fi
            if [[ $line == "\"num_2F"* ]]; then
                [[ ${line:10:4} =~ ^.[0-9]* ]] && num_2F=$BASH_REMATCH
            fi
            if [[ $line == "\"num_1M"* ]]; then
                [[ ${line:10:4} =~ ^.[0-9]* ]] && num_1M=$BASH_REMATCH
            fi
            if [[ $line == "\"num_2M"* ]]; then
                [[ ${line:10:4} =~ ^.[0-9]* ]] && num_2M=$BASH_REMATCH
            fi
        done < $f
        echo "$set;$avg_acc;$avg_acc_f;$avg_acc_m;$avg_acc_cat;$avg_acc_1F;$avg_acc_2F;$avg_acc_1M;$avg_acc_2M;$num_f;$num_m;$num_1F;$num_2F;$num_1M;$num_2M" >> $out
    done
done


# pivot
for ref in correct_ref wrong_ref; do
    DIRPATH=$OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref
    for sl in en es it fr; do
        for tl in es it fr; do
            if [ "$sl" != "$tl" ] && [ "$sl" != "$PIVOT" ] && [ "$tl" != "$PIVOT" ]; then
                python3 -u $NMTDIR/utils/eval_gender_accuracy.py \
                        -pred_path $DIRPATH/$sl-$PIVOT-$tl.real.pivotout.t.pt \
                        -gterms_path $DATADIR/mustshe/raw/$ref/add_info/${tl}_gterms.csv \
                        -speaker_path $DATADIR/mustshe/raw/$ref/add_info/${tl}_speaker.csv \
                        -category_path $DATADIR/mustshe/raw/$ref/add_info/${tl}_category.csv \
                        -stats_path $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref/$sl-$PIVOT-$tl.stats.json
            fi
        done
    done
    out=/home/lperez/output/results_gender_acc_${TRAIN_SET}_${ref}_pivot.csv
    rm -f $out
    echo "set;avg_acc;avg_acc_f;avg_acc_m;avg_acc_cat;avg_acc_1F;avg_acc_2F;avg_acc_1M;avg_acc_2M;num_f;num_m;num_1F;num_2F;num_1M;num_2M" >> $out
    for f in $DIRPATH/*\.json; do
        filename="$(basename "$f")"
        [[ ${filename} =~ [a-z][a-z]-[a-z][a-z]-[a-z][a-z] ]] && set=$BASH_REMATCH
        while read -r line; do 
            if [[ $line == "\"avg__acc"* ]]; then
                [[ ${line:12:4} =~ ^.[0-9]*.[0-9]* ]] && avg_acc=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_f"* ]]; then
                [[ ${line:13:4} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_f=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_m"* ]]; then
                [[ ${line:13:4} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_m=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_cat"* ]]; then
                [[ ${line:15:4} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_cat=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_1F"* ]]; then
                [[ ${line:14:5} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_1F=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_2F"* ]]; then
                [[ ${line:14:5} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_2F=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_1M"* ]]; then
                [[ ${line:14:5} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_1M=$BASH_REMATCH
            fi
            if [[ $line == "\"avg_acc_2M"* ]]; then
                [[ ${line:14:5} =~ ^.[0-9]*.[0-9]* ]] && avg_acc_2M=$BASH_REMATCH
            fi

            if [[ $line == "\"num_f"* ]]; then
                [[ ${line:9:4} =~ ^.[0-9]* ]] && num_f=$BASH_REMATCH
            fi
            if [[ $line == "\"num_m"* ]]; then
                [[ ${line:9:4} =~ ^.[0-9]* ]] && num_m=$BASH_REMATCH
            fi
            if [[ $line == "\"num_1F"* ]]; then
                [[ ${line:10:4} =~ ^.[0-9]* ]] && num_1F=$BASH_REMATCH
            fi
            if [[ $line == "\"num_2F"* ]]; then
                [[ ${line:10:4} =~ ^.[0-9]* ]] && num_2F=$BASH_REMATCH
            fi
            if [[ $line == "\"num_1M"* ]]; then
                [[ ${line:10:4} =~ ^.[0-9]* ]] && num_1M=$BASH_REMATCH
            fi
            if [[ $line == "\"num_2M"* ]]; then
                [[ ${line:10:4} =~ ^.[0-9]* ]] && num_2M=$BASH_REMATCH
            fi
        done < $f
        echo "$set;$avg_acc;$avg_acc_f;$avg_acc_m;$avg_acc_cat;$avg_acc_1F;$avg_acc_2F;$avg_acc_1M;$avg_acc_2M;$num_f;$num_m;$num_1F;$num_2F;$num_1M;$num_2M" >> $out
    done
done