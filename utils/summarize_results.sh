#!/bin/bash
MODEL=transformer.mustc

out_path=$NMTDIR/../output/results_auto
out_path_pkl=$NMTDIR/../output/results_auto/pkl
out_path_json=$NMTDIR/../output/results_auto/json
out_path_csv=$NMTDIR/../output/results_auto/csv

mkdir -p $out_path
mkdir -p $out_path_pkl
mkdir -p $out_path_json
mkdir -p $out_path_csv

python3 -u $NMTDIR/utils/create_results_data_frames.py \
        -in_path $out_path/xlsx \
        -out_path $out_path_pkl

rm -f $out_path_csv/summary_bleu.csv
rm -f $out_path_csv/summary_acc.csv
rm -f $out_path_csv/summary_acc_cat.csv
rm -f $out_path_csv/summary_acc_speaker.csv

# multiway
small_baseline_EN="multiwayEN"
small_residual_EN="multiwayEN.r32.q"
small_baseline_EN_AUX="multiwayEN.SIM"
small_residual_EN_AUX="multiwayEN.SIM.r32.q"
small_baseline_EN_ADV="multiwayEN.ADV"
small_residual_EN_ADV="multiwayEN.ADV.r32.q"

small_train_b_en="${small_baseline_EN} ${small_baseline_EN_AUX} ${small_baseline_EN_ADV}"
small_train_r_en="${small_residual_EN} ${small_residual_EN_AUX} ${small_residual_EN_ADV}"
small_train_en="${small_train_b_en} ${small_train_r_en}"

# twoway
baseline_EN="twoway.r32.q"
residual_EN="twoway.r32.q.new"
baseline_EN_AUX="twoway.SIM"
residual_EN_AUX="twoway.SIM.r32.q"
baseline_EN_ADV="twoway.ADV.GEN" # "twoway.new.ADV" # "twoway.ADV.GEN"
residual_EN_ADV="twoway.ADV.GEN.r32.q" # "twoway.new.ADV.r32.q" # "twoway.ADV.GEN.r32.q"

baseline_ES="twowayES"
residual_ES="twowayES.r32.q"
baseline_ES_AUX="twowayES.SIM"
residual_ES_AUX="twowayES.SIM.r32.q"
baseline_ES_ADV="twowayES.new.ADV"
residual_ES_ADV="twowayES.new.ADV.r32.q"

baseline_DE="twowayDE"
residual_DE="twowayDE.r32.q"
baseline_DE_AUX="twowayDE.SIM"
residual_DE_AUX="twowayDE.SIM.r32.q"
baseline_DE_ADV="twowayDE.new.ADV"
residual_DE_ADV="twowayDE.new.ADV.r32.q"

train_twoway_b_en="${baseline_EN} ${baseline_EN_AUX} ${baseline_EN_ADV}"
train_twoway_r_en="${residual_EN} ${residual_EN_AUX} ${residual_EN_ADV}"
train_twoway_en="${train_twoway_b_en} ${train_twoway_r_en}"

train_twoway_b_es="${baseline_ES} ${baseline_ES_AUX} ${baseline_ES_ADV}"
train_twoway_r_es="${residual_ES} ${residual_ES_AUX} ${residual_ES_ADV}"
train_twoway_es="${train_twoway_b_es} ${train_twoway_r_es}"

train_twoway_b_de="${baseline_DE} ${baseline_DE_AUX} ${baseline_DE_ADV}"
train_twoway_r_de="${residual_DE} ${residual_DE_AUX} ${residual_DE_ADV}"
train_twoway_de="${train_twoway_b_de} ${train_twoway_r_de}"

train_twoway="${train_twoway_en} ${train_twoway_es} ${train_twoway_de}"
train_sets="${train_twoway}"

# # # *** mustshe ***
# # for train_set in $train_sets; do
# for train_set in $train_sets; do
#     echo $train_set
#     python3 -u $NMTDIR/utils/prep_results.py \
#             -raw_path $DATADIR/mustshe/raw \
#             -pred_path $OUTDIR/$MODEL/mustshe/$train_set \
#             -train_set $train_set \
#             -df_path $out_path_pkl \
#             -out_path_json $out_path_json \
#             -out_path_csv $out_path_csv \
#             -out_path $out_path
# done


# # *** mustc ***
TEST_SET="mustc"
for train_set in $train_sets; do
    path=$OUTDIR/$MODEL/$TEST_SET/$train_set/
    path_pivot=$OUTDIR/$MODEL/$TEST_SET/$train_set/pivot
    echo $train_set
    # direct
    out_exp=/home/lperez/output/$train_set/$TEST_SET/direct
    rm -fr $out_exp
    mkdir -p $out_exp
    for f in $path/*\.pt; do
            cp $f $out_exp
    done
    # pivot
    out_exp_piv=/home/lperez/output/$train_set/$TEST_SET/pivot
    rm -fr $out_exp_piv
    mkdir -p $out_exp_piv
    for f in $path_pivot/*\.pt; do
            cp $f $out_exp_piv
    done
        
    if [[ $TEST_SET == "mustc" ]]; then
        # direct
        out=/home/lperez/output/results_${TEST_SET}_${train_set}.csv
        rm -f $out
        for f in $path/*\.res; do
            while read -r line; do 
                if [[ $line == "\"score"* ]]; then
                    filename="$(basename "$f")"
                    [[ ${filename} =~ [a-z][a-z]-[a-z][a-z] ]] && set=$BASH_REMATCH
                    [[ ${line:9:4} =~ ^.[0-9]*.[0-9]* ]] && score=$BASH_REMATCH
                    echo "$set;$score" >> $out
                fi
            done < $f
        done
        # pivot
        out_piv=/home/lperez/output/results_${TEST_SET}_${train_set}_pivot.csv
        rm -f $out_piv
        for f in $path_pivot/*\.res; do
            while read -r line; do 
                if [[ $line == "\"score"* ]]; then
                    filename="$(basename "$f")"
                    [[ ${filename} =~ [a-z][a-z]-[a-z][a-z]-[a-z][a-z] ]] && set=$BASH_REMATCH
                    [[ ${line:9:4} =~ ^.[0-9]*.[0-9]* ]] && score=$BASH_REMATCH
                    echo "$set;$score" >> $out_piv
                fi
            done < $f
        done
    fi
done
