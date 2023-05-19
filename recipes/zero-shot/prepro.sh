#!/bin/bash
# export systemName=pmIndia #.star.9
export systemName=iwslt17_multiway
export BPESIZE=20000
export PREPRO_TYPE=${BPESIZE}
export INDIC_TOKENIZER="bash $FLORESDIR/floresv1/scripts/indic_norm_tok.sh"
export SENTENCE_PIECE=false  # only for indic data

if [ $SENTENCE_PIECE = true ]; then
        PREPRO_TYPE=${PREPRO_TYPE}_sentencepiece
else
        PREPRO_TYPE=${PREPRO_TYPE}_subwordnmt
fi

PREPRO_DIR=prepro_${PREPRO_TYPE}

$SCRIPTDIR/scripts/defaultPreprocessor/Train.sh $systemName $PREPRO_DIR

# IWSLT languages
for sl in en it nl ro; do
        for tl in en it nl ro; do
                if [ "$sl" != "$tl" ]; then
                        export sl=$sl
                        export tl=$tl
                        echo $sl-$tl
                        $SCRIPTDIR/scripts/defaultPreprocessor/Translate.sh $sl-$tl $PREPRO_DIR $systemName
                fi
        done
done

python -u $NMTDIR/utils/add_tl_specific_token.py $DATADIR/$systemName/$PREPRO_DIR/ iwslt
