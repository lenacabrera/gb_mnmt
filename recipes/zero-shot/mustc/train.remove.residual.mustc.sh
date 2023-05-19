#!/bin/bash
source ../config.sh

export systemName=mustc
export TRAIN_SET=multiwayES  # twoway, multiwayES

export BASEDIR=$WORKDIR
export LAYER=5
export TRANSFORMER=transformer
export ENC_LAYER=5
export WUS=8000
export HEAD=8

# data setup
export PREPRO_DIR=$systemName/prepro_20000_subwordnmt/$TRAIN_SET
export EPOCHS=64
export LR=2

export LAN_EMB=true
export LAN_EMB_CONCAT=true

export RESIDUAL_AT=3
export RESIDUAL=2 #1: meanpool, 2: no residual

export SKIP_PREPRO=true

export FP16=true
export MODEL=$TRANSFORMER.$PREPRO_DIR.r${RESIDUAL_AT}${RESIDUAL}.q${QUERY_AT}${QUERY}

# Start training
echo 'Start training'
echo $PREPRO_DIR

mkdir -p $BASEDIR/model/${MODEL}

for f in $DATADIR/$PREPRO_DIR/binarized_mmem/*; do
        ln -s $f $WORKDIR/model/${MODEL}/$(basename -- "$fullfile")
done

$SCRIPTDIR/mustc/utils/train.mustc.sh $PREPRO_DIR $MODEL

echo 'Done training'
