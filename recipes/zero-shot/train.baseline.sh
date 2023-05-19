#!/bin/bash
source ./config.sh

export systemName=pmIndia.star.9

export BASEDIR=$WORKDIR/$systemName/
export LAYER=5
export TRANSFORMER=transformer
export ENC_LAYER=5
export WUS=8000
export HEAD=8

# data setup
export PREPRO_DIR=prepro_40000_sentencepiece
export EPOCHS=64
export LR=2

export SKIP_TRAIN=false
export MULTILAN=true   # CHECK
export LAN_EMB=true
export LAN_EMB_CONCAT=true

export SKIP_PREPRO=true

export FP16=true
export MODEL=$TRANSFORMER.$PREPRO_DIR

# Start training
echo 'Start training'
echo $PREPRO_DIR

mkdir $BASEDIR/model/${MODEL} -p

for f in $BASEDIR/data/$PREPRO_DIR/binarized_mmem/*; do
        ln -s $f $BASEDIR/model/${MODEL}/$(basename -- "$fullfile")
done

$SCRIPTDIR/train.sh $PREPRO_DIR $MODEL

echo 'Done training'
