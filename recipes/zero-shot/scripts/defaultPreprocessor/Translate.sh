#!/bin/bash

set=$1      # language pair
name=$2     # prepro dir
origname=$3 # systemName


if [ -z "$MOSESDIR" ]; then
    MOSESDIR=/opt/mosesdecoder/
fi

if [ -z "$BPEDIR" ]; then
    BPEDIR=/opt/subword-nmt/
fi

if [ -z "$SRC_INDIC" ]; then
    SRC_INDIC=false
fi

if [ -z "$origname" ]; then
    origname=orig
fi


mkdir -p $WORKDIR/data/${origname}/${name}/test/


xml=0
if [ -f $WORKDIR/data/$origname/eval/$set/IWSLT.$set/IWSLT.TED.$set.$sl-$tl.$sl.xml ]; then
    inFile=$WORKDIR/data/$origname/eval/$set/IWSLT.$set/IWSLT.TED.$set.$sl-$tl.$sl.xml
    xml=1
elif [ -f $WORKDIR/data/$origname/eval/$set.s ]; then
    inFile=$WORKDIR/data/$origname/eval/$set.s
    xml=0
elif [ -f $WORKDIR/data/$origname/raw/test/prep/$set.s ]; then
    # iwslt17_multiway
    inFile=$WORKDIR/data/$origname/raw/test/prep/$set.s
    xml=0
elif [ -f $WORKDIR/data/$origname/raw/tst-COMMON/$set.s ]; then
    # MuST-C data  
    echo "mustc"
    inFile=$WORKDIR/data/$origname/raw/tst-COMMON/$set.s
    xml=0
fi
echo "inFile: " $inFile

# TOKENIZE, SMARTCASE, BPE
if [ $xml -eq 1 ]; then
    cat $inFile | grep "<seg id" | sed -e "s/<[^>]*>//g" | \
        perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${sl} | \
        $MOSESDIR/scripts/recaser/truecase.perl --model $WORKDIR/model/${name}/${origname}/truecase-model.s | \
        $BPEDIR/apply_bpe.py -c $WORKDIR/model/${name}/${origname}/codec --vocabulary $WORKDIR/model/${name}/${origname}/voc.s --vocabulary-threshold 50 \
                    > $WORKDIR/data/${name}/eval/manualTranscript.$set.s
else
    sl=${set:0:2}
    echo $sl
    if [ ! "$SENTENCE_PIECE" == true ]; then
        cat $inFile | \
            perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${sl} | \
            $MOSESDIR/scripts/recaser/truecase.perl --model $WORKDIR/model/${name}/${origname}/truecase-model.s | \
            $BPEDIR/subword_nmt/apply_bpe.py -c $WORKDIR/model/${name}/${origname}/codec --vocabulary $WORKDIR/model/${name}/${origname}/voc.s --vocabulary-threshold 50 \
                > $WORKDIR/data/${origname}/${name}/test/$set.s
                        # > $WORKDIR/data/${origname}/raw/train/$set.s
    else
        if [ "$sl" != 'ml' ] && [ "$sl" != 'te' ]  && [ "$sl" != 'kn' ] && [ "$sl" != 'ta' ] && [ "$sl" != 'bn' ] && [ "$sl" != 'gu' ] && [ "$sl" != 'hi' ] && [ "$sl" != 'mr' ] && [ "$sl" != 'or' ] && [ "$sl" != 'pa' ]; then
            cat $inFile | perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${sl} | \
                $MOSESDIR/scripts/recaser/truecase.perl --model $WORKDIR/model/${name}/${origname}/truecase-model.s > $WORKDIR/data/${name}/eval/$set.tok.s
        else
            $INDIC_TOKENIZER ${sl} $inFile > $WORKDIR/data/${name}/eval/$set.tok.s
        fi

        # spm_encode \
        # 	--model=$WORKDIR/data/${name}/sentencepiece.bpe.model \
        #         --output_format=piece \
        #         --vocabulary_threshold 50 < $WORKDIR/data/${name}/eval/$set.tok.s > $WORKDIR/data/${name}/eval/$set.s

        # python $FLORES_SCRIPTS/spm_encode.py \
        #                --model $WORKDIR/data/${name}/sentencepiece.bpe.model \
        #                --output_format=piece \
        #                --inputs $WORKDIR/data/${name}/eval/$set.tok.s \
        #                --outputs $WORKDIR/data/${name}/eval/$set.s

    fi
fi
