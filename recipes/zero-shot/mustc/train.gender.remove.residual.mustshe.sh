# #!/bin/bash
# source ./config.sh

export systemName=mustshe
export TRAIN_SET=twowayES  # {twoway, twowayES, twowayDE} + {.SIM, .ADV}

export BASEDIR=$WORKDIR
export LAYER=5
export TRANSFORMER=transformer
export ENC_LAYER=5
export WUS=400
export HEAD=8

export EPOCHS=10

# data setup
export PREPRO_DIR=$systemName/prepro_20000_subwordnmt/$TRAIN_SET.GEN
export LR=2

export SKIP_TRAIN=false
export MULTILAN=true
export LAN_EMB=true
export LAN_EMB_CONCAT=true

export RESIDUAL_AT=3
export RESIDUAL=2 #1: meanpool, 2: no residual

export SKIP_PREPRO=true

export FP16=true
export MODEL=$TRANSFORMER.$PREPRO_DIR.r${RESIDUAL_AT}${RESIDUAL}.q${QUERY_AT}${QUERY}
# export MODEL=$TRANSFORMER.$PREPRO_DIR

export CLASSIFICATION_TYPE=0 # gender clf

# Start training
echo 'Start training'
# echo $PREPRO_DIR
# echo $MODEL

mkdir $WORKDIR/model/${MODEL} -p

# for f in $DATADIR/$PREPRO_DIR/binarized_mmem/*; do
for f in $DATADIR/$systemName/prepro_20000_subwordnmt/twoway.GEN/binarized_mmem/*; do
        ln -s -f $f $WORKDIR/model/${MODEL}/$(basename -- "$fullfile")
done

$SCRIPTDIR/mustc/utils/train.gender.mustc.sh $PREPRO_DIR $MODEL
echo 'Done training'
