#!/bin/bash
export systemName=mustc
export BPESIZE=20000
export PREPRO_TYPE=${BPESIZE}
export SENTENCE_PIECE=false
export REMOVE_OVERLAP_W_MUSTSHE=true

if [ $SENTENCE_PIECE = true ]; then
        PREPRO_TYPE=${PREPRO_TYPE}_sentencepiece
else
        PREPRO_TYPE=${PREPRO_TYPE}_subwordnmt
fi

PREPRO_DIR=prepro_${PREPRO_TYPE}

echo "Prepare raw data..."
$SCRIPTDIR/mustc/utils/prepare.mustc.sh $REMOVE_OVERLAP_W_MUSTSHE

echo "Preprocessing 2-way data..."
$SCRIPTDIR/mustc/utils/train.preprocessor.mustc.sh $systemName $PREPRO_DIR twoway

# # MuST-C languages: ar cs de en es fa fr it nl pt ro ru tr vi zh -> languages not supported by moses tokenizer: ar, fa, tr, vi, zh
LAN="cs de en es fr it nl pt ro ru" # lang. supported by moses tokenizer

for sl in $LAN; do
        for tl in $LAN; do
                if [ "$sl" != "$tl" ]; then
                        echo $sl-$tl
                        export sl=$sl
                        export tl=$tl
                        $SCRIPTDIR/mustc/utils/apply.preprocessor.mustc.sh $sl-$tl $PREPRO_DIR $systemName twoway
                fi
        done
done

echo "Add target language specific bos token..."
python -u $NMTDIR/utils/add_tl_specific_token.py $DATADIR/mustc/$PREPRO_DIR/twoway/ mustc_twoway

echo "Preprocessing multi-way data..."
$SCRIPTDIR/mustc/utils/train.preprocessor.mustc.sh $systemName $PREPRO_DIR multiway

for sl in $LAN; do
        for tl in $LAN; do
                if [ "$sl" != "$tl" ]; then
                        echo $sl-$tl
                        export sl=$sl
                        export tl=$tl
                        $SCRIPTDIR/mustc/utils/apply.preprocessor.mustc.sh $sl-$tl $PREPRO_DIR $systemName multiway
                fi
        done
done

echo "Add target language specific bos token..."
python -u $NMTDIR/utils/add_tl_specific_token.py $DATADIR/mustc/$PREPRO_DIR/multiway/ mustc_multiway
