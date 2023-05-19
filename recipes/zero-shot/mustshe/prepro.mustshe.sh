#!/bin/bash
export systemName=mustc
export BPESIZE=20000
export PREPRO_TYPE=${BPESIZE}
export SENTENCE_PIECE=false
export REMOVE_OVERLAP_W_MUSTC=true

TRAIN_SET=multiway
# TRAIN_SET=twoway

if [ $SENTENCE_PIECE = true ]; then
        PREPRO_TYPE=${PREPRO_TYPE}_sentencepiece
else
        PREPRO_TYPE=${PREPRO_TYPE}_subwordnmt
fi
PREPRO_DIR=prepro_${PREPRO_TYPE}
TOKDIR=$DATADIR/mustshe/$PREPRO_DIR/$TRAIN_SET    # path to tokenized data

mkdir -p $TOKDIR
mkdir -p $TOKDIR/correct_ref
mkdir -p $TOKDIR/correct_ref/all
mkdir -p $TOKDIR/correct_ref/feminine
mkdir -p $TOKDIR/correct_ref/masculine
mkdir -p $TOKDIR/wrong_ref
mkdir -p $TOKDIR/wrong_ref/all
mkdir -p $TOKDIR/wrong_ref/feminine
mkdir -p $TOKDIR/wrong_ref/masculine

echo "Prepare raw data..."
bash $SCRIPTDIR/mustshe/prepare.mustshe.sh $REMOVE_OVERLAP_W_MUSTC

echo "Preprocessing with previously trained BPE..."
for ref in correct_ref wrong_ref; do
        for gender_set in all feminine masculine; do
                for sl in en es it fr; do
                        for tl in  en es it fr; do
                                if [ "$sl" != "$tl" ]; then
                                        set=$sl-$tl
                                        tok_file=$TOKDIR/$ref/$gender_set/$set.s
                                        src_file=$DATADIR/mustshe/raw/$ref/$gender_set/$set.s
                                        cat $src_file | \
                                                perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${sl} | \
                                                $MOSESDIR/scripts/recaser/truecase.perl --model $WORKDIR/model/$PREPRO_DIR/mustc/$TRAIN_SET/truecase-model.s | \
                                                $BPEDIR/subword_nmt/apply_bpe.py -c $WORKDIR/model/$PREPRO_DIR/mustc/$TRAIN_SET/codec --vocabulary $WORKDIR/model/$PREPRO_DIR/mustc/$TRAIN_SET/voc.s --vocabulary-threshold 50 \
                                                        > $tok_file
                                fi
                        done
                done
        done
done
