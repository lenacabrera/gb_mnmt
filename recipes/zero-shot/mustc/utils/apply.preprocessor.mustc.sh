#!/bin/bash

set=$1      # language pair
prepro_name=$2     # prepro dir
input=$3 # systemName
nway=$4


if [ -z "$MOSESDIR" ]; then
    MOSESDIR=/opt/mosesdecoder/
fi

if [ -z "$BPEDIR" ]; then
    BPEDIR=/opt/subword-nmt/
fi

if [ -z "$SRC_INDIC" ]; then
    SRC_INDIC=false
fi

if [ -z "$input" ]; then
    input=orig
fi


mkdir -p $WORKDIR/data/${input}/${prepro_name}/${nway}/test/


xml=0
echo $WORKDIR/data/$input/raw/${nway}/tst-COMMON/$set.s
if [ -f $WORKDIR/data/$input/raw/${nway}/tst-COMMON/$set.s ]; then
    inFile=$WORKDIR/data/$input/raw/${nway}/tst-COMMON/$set.s
    xml=0
fi
echo "inFile: " $inFile

# TOKENIZE, SMARTCASE, BPE
sl=${set:0:2}
echo $sl
if [ ! "$SENTENCE_PIECE" == true ]; then
    cat $inFile | \
        perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${sl} | \
        $MOSESDIR/scripts/recaser/truecase.perl --model $WORKDIR/model/${prepro_name}/${input}/${nway}/truecase-model.s | \
        $BPEDIR/subword_nmt/apply_bpe.py -c $WORKDIR/model/${prepro_name}/${input}/${nway}/codec --vocabulary $WORKDIR/model/${prepro_name}/${input}/${nway}/voc.s --vocabulary-threshold 50 \
            > $WORKDIR/data/${input}/${prepro_name}/${nway}/test/$set.s
else
    if [ "$sl" != 'ml' ] && [ "$sl" != 'te' ]  && [ "$sl" != 'kn' ] && [ "$sl" != 'ta' ] && [ "$sl" != 'bn' ] && [ "$sl" != 'gu' ] && [ "$sl" != 'hi' ] && [ "$sl" != 'mr' ] && [ "$sl" != 'or' ] && [ "$sl" != 'pa' ]; then
        cat $inFile | perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${sl} | \
            $MOSESDIR/scripts/recaser/truecase.perl --model $WORKDIR/model/${prepro_name}/${input}/${nway}/truecase-model.s > $WORKDIR/data/${prepro_name}/eval/$set.tok.s
    fi
    # spm_encode \
    # 	--model=$WORKDIR/data/${prepro_name}/sentencepiece.bpe.model \
    #         --output_format=piece \
    #         --vocabulary_threshold 50 < $WORKDIR/data/${prepro_name}/eval/$set.tok.s > $WORKDIR/data/${prepro_name}/eval/$set.s

    # python $FLORES_SCRIPTS/spm_encode.py \
    #                --model $WORKDIR/data/${prepro_name}/sentencepiece.bpe.model \
    #                --output_format=piece \
    #                --inputs $WORKDIR/data/${prepro_name}/eval/$set.tok.s \
    #                --outputs $WORKDIR/data/${prepro_name}/eval/$set.s

fi
