# models

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

small_baseline_ES="multiwayES"
small_residual_ES="multiwayES.r32.q"
small_baseline_ES_AUX="multiwayES.SIM"
small_residual_ES_AUX="multiwayES.SIM.r32.q"
small_baseline_ES_ADV="multiwayES.ADV"
small_residual_ES_ADV="multiwayES.ADV.r32.q"

small_train_b_es="${small_baseline_ES} ${small_baseline_ES_AUX} ${small_baseline_ES_ADV}"
small_train_r_es="${small_residual_ES} ${small_residual_ES_AUX} ${small_residual_ES_ADV}"
small_train_es="${small_train_b_es} ${small_train_r_es}"

# twoway
# baseline_EN="twoway.r32.q"
# residual_EN="twoway.r32.q.new"
# baseline_EN_AUX="twoway.SIM"
# residual_EN_AUX="twoway.SIM.r32.q"
# baseline_EN_ADV="twoway.new.ADV"
# residual_EN_ADV="twoway.new.ADV.r32.q"

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


# train_sets="${small_train_es}"

# mustshe
# for train_set in ${baseline_DE_ADV} $residual_DE_ADV; do
# # for train_set in $train_twoway_r_en  ${baseline_EN_ADV} $baseline_EN; do
#     echo $train_set

#     # pick correct eval set -> tokenization based on training data
#     eval_set=twoway
#     if [[ $train_twoway_en == *$train_set* ]]; then
#         eval_set=twoway
#         pivot=en
#     elif [[ $train_twoway_es == *$train_set* ]]; then
#         eval_set=twowayES
#         pivot=es
#     elif [[ $train_twoway_de == *$train_set* ]]; then
#         eval_set=twowayDE
#         pivot=de
#     elif [[ $small_train_en == *$train_set* ]]; then
#         eval_set=multiwayEN
#         pivot=en
#     elif [[ $small_train_es == *$train_set* ]]; then
#         eval_set=multiwayES
#         pivot=es
#     else
#         echo "Error: Unknown model"
#         exit
#     fi

#     echo $train_set $eval_set
#     # zero-shot
#     bash $SCRIPTDIR/mustshe/pred.mustshe.sh transformer.mustc $train_set $eval_set
#     # pivot
#     # bash $SCRIPTDIR/mustshe/pred.pivot.mustshe.sh transformer.mustc $pivot $train_set $eval_set
# done


# mustc
# for train_set in $train_sets; do
for train_set in $train_sets; do
    echo $train_set
    # pick correct eval set -> tokenization based on training data
    EVAL_SET=multiway
    if [[ $train_twoway_en == *$train_set* ]]; then
        eval_set=twoway
        pivot=en
    elif [[ $train_twoway_es == *$train_set* ]]; then
        eval_set=twowayES
        pivot=es
    elif [[ $train_twoway_de == *$train_set* ]]; then
        eval_set=twowayDE
        pivot=de
    else
        echo "Error: Unknown model"
        exit
    fi

    # zero-shot
    bash $SCRIPTDIR/mustc/pred.mustc.sh transformer.mustc $train_set $EVAL_SET
    echo PIVOT $train_set
    if [[ $train_twoway_en == *$train_set* ]]; then
        pivot=en
    elif [[ $train_twoway_es == *$train_set* ]]; then
        pivot=es
    elif [[ $train_twoway_de == *$train_set* ]]; then
        pivot=de
    else
        echo "Error: Unknown model"
        exit
    fi
    pivot
    bash $SCRIPTDIR/mustc/pred.pivot.mustc.sh transformer.mustc $pivot $train_set $EVAL_SET
done
