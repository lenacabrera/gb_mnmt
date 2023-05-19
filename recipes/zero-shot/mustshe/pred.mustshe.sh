#!/bin/bash
source ./recipes/zero-shot/config.sh
set -eu

export MODEL=$1 # model name, e.g. transformer.mustc
export TRAIN_SET=$2         # e.g. twoway.SIM
export EVAL_SET=$3          # e.g. twoway
export PREPRO_DIR=prepro_20000_subwordnmt

if [ -z "$EVAL_SET" ]; then
    EVAL_SET=twoway
fi

LAN="en es it fr"
# LAN="fr it"

mkdir $OUTDIR/$MODEL/mustshe -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/correct_ref -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/correct_ref/all -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/correct_ref/feminine -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/correct_ref/masculine -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/wrong_ref -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/wrong_ref/all -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/wrong_ref/feminine -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/wrong_ref/masculine -p

# compare results for correct and wrong reference to determine bias
for ref in correct_ref wrong_ref; do  
    for gender_set in all feminine masculine; do
        for sl in $LAN; do
            for tl in $LAN; do
                if [[ ! "$sl" == "$tl" ]]; then

                    echo $sl "->" $tl

                    # pred_src=$DATADIR/mustshe/$PREPRO_DIR/$ref/$gender_set/$sl-$tl.s # path to tokenized test data
                    pred_src=$DATADIR/mustshe/$PREPRO_DIR/$EVAL_SET/correct_ref/$gender_set/$sl-$tl.s # path to tokenized test data
                    out=$OUTDIR/$MODEL/mustshe/$TRAIN_SET/$ref/$gender_set/$sl-$tl.pred
                    echo $pred_src
                    bos='#'${tl^^}  # beginning of sentence token: target language

                    python3 -u $NMTDIR/translate.py \
                            -gpu $GPU \
                            -model $WORKDIR/model/$MODEL/$PREPRO_DIR/$TRAIN_SET/model.pt \
                            -src $pred_src \
                            -batch_size 128 \
                            -verbose \
                            -beam_size 4 \
                            -alpha 1.0 \
                            -normalize \
                            -output $out \
                            -fast_translate \
                            -src_lang $sl \
                            -tgt_lang $tl \
                            -bos_token $bos
                    
                    # Postprocess output
                    sed -e "s/@@ //g" $out  | sed -e "s/@@$//g" | sed -e "s/&apos;/'/g" -e 's/&#124;/|/g' -e "s/&amp;/&/g" -e 's/&lt;/>/g' -e 's/&gt;/>/g' -e 's/&quot;/"/g' -e 's/&#91;/[/g' -e 's/&#93;/]/g' -e 's/ - /-/g' | sed -e "s/ '/'/g" | sed -e "s/ '/'/g" | sed -e "s/%- / -/g" | sed -e "s/ -%/- /g" | perl -nle 'print ucfirst' > $out.tok
                    
                    $MOSESDIR/scripts/tokenizer/detokenizer.perl -l $tl < $out.tok > $out.detok
                    $MOSESDIR/scripts/recaser/detruecase.perl < $out.detok > $out.pt
                    
                    rm $out.tok $out.detok
                
                    echo '===========================================' $sl $tl
                    # Evaluate against original reference  
                    cat $out.pt | sacrebleu $DATADIR/mustshe/raw/$ref/$gender_set/$sl-$tl.t > $OUTDIR/$MODEL/mustshe/$TRAIN_SET/$ref/$gender_set/$sl-$tl.res
                    cat $OUTDIR/$MODEL/mustshe/$TRAIN_SET/$ref/$gender_set/$sl-$tl.res
                
                fi
            done
        done
    done
done
