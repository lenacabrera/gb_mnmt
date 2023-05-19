#!/bin/bash
source ./recipes/zero-shot/config.sh

export MODEL=$1
export PIVOT=$2
export TRAIN_SET=$3
export EVAL_SET=$4
export PREPRO_DIR=prepro_20000_subwordnmt

if [ -z "$PIVOT" ]; then
    PIVOT=en
fi

if [ -z "$TRAIN_SET" ]; then
    TRAIN_SET=twoway
fi

if [ -z "$EVAL_SET" ]; then
    EVAL_SET=multiway
fi

mkdir $OUTDIR/$MODEL/mustc -p
mkdir $OUTDIR/$MODEL/mustc/$TRAIN_SET -p
mkdir $OUTDIR/$MODEL/mustc/$TRAIN_SET/pivot -p


LAN="cs de en es fr it nl pt ro ru"

for src in $LAN; do
    for tgt in $LAN; do
        if [[ $src != $tgt ]] && [[ $src != $PIVOT ]] && [[ $tgt != $PIVOT ]]; then
        
            echo $src " -> " $PIVOT " -> " $tgt

            # (1) pivot into e.g. English
            export sl=$src
            export tl=$PIVOT

            ln -s -f $DATADIR/mustc/$PREPRO_DIR/$EVAL_SET/test/$sl-$tl.s  $OUTDIR/$MODEL/mustc/$TRAIN_SET/pivot/${src}-$PIVOT-${tgt}.real.pivotin.s 
            
            pred_src=$OUTDIR/$MODEL/mustc/$TRAIN_SET/pivot/${src}-$PIVOT-${tgt}.real.pivotin.s
            out=$OUTDIR/$MODEL/mustc/$TRAIN_SET/pivot/${src}-$PIVOT-${tgt}.real.pivotin.t

            bos='#'${tl^^}

            echo "Translate to pivot..."
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

            # (2) pivot out of English
            export sl=$PIVOT
            export tl=$tgt

            ln -s -f $OUTDIR/$MODEL/mustc/$TRAIN_SET/pivot/${src}-$PIVOT-${tgt}.real.pivotin.t $OUTDIR/$MODEL/mustc/$TRAIN_SET/pivot/${src}-$PIVOT-${tgt}.real.pivotout.s

            pred_src=$OUTDIR/$MODEL/mustc/$TRAIN_SET/pivot/${src}-$PIVOT-${tgt}.real.pivotout.s
            out=$OUTDIR/$MODEL/mustc/$TRAIN_SET/pivot/${src}-$PIVOT-${tgt}.real.pivotout.t

            bos='#'${tl^^}

            echo "Translate from pivot..."
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

            sed -e "s/@@ //g" $out  | sed -e "s/@@$//g" | sed -e "s/&apos;/'/g" -e 's/&#124;/|/g' -e "s/&amp;/&/g" -e 's/&lt;/>/g' -e 's/&gt;/>/g' -e 's/&quot;/"/g' -e 's/&#91;/[/g' -e 's/&#93;/]/g' -e 's/ - /-/g' | sed -e "s/ '/'/g" | sed -e "s/ '/'/g" | sed -e "s/%- / -/g" | sed -e "s/ -%/- /g" | perl -nle 'print ucfirst' > $out.tok

            $MOSESDIR/scripts/tokenizer/detokenizer.perl -l $tl < $out.tok > $out.detok
            $MOSESDIR/scripts/recaser/detruecase.perl < $out.detok > $out.pt

            rm $out.tok $out.detok

            echo '===========================================' $src $tgt
            # Evaluate against original reference  
            cat $out.pt | sacrebleu $DATADIR/mustc/raw/$EVAL_SET/tst-COMMON/$src-$tgt.t > $out.res
            cat $out.res
        fi
    done
done

