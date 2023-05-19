#!/bin/bash
source ./recipes/zero-shot/config.sh
set -eu

export MODEL=$1 # model name
export PIVOT=$2
export TRAIN_SET=$3
export EVAL_SET=$4
export PREPRO_DIR=prepro_20000_subwordnmt

if [ -z "$EVAL_SET" ]; then
    EVAL_SET=twoway
fi

LAN="en es it fr"

mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/correct_ref -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/correct_ref/all -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/correct_ref/feminine -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/correct_ref/masculine -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/wrong_ref -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/wrong_ref/all -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/wrong_ref/feminine -p
mkdir $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/wrong_ref/masculine -p

# compare results for correct and wrong reference to determine bias
for ref in correct_ref wrong_ref; do  
    for gender_set in all feminine masculine; do
        for src in $LAN; do
            for tgt in $LAN; do
                if [[ $src != $tgt ]] && [[ $src != $PIVOT ]] && [[ $tgt != $PIVOT ]]; then
                    
                    echo $src " -> $PIVOT -> " $tgt

                    # (1) pivot into English
                    export sl=$src
                    export tl=$PIVOT

                    if [[ $PIVOT == de ]]; then
                        echo $PIVOT
                        for suplementl in $LAN; do
                            if [[ $suplementl != $sl ]] && [[ $suplementl != $PIVOT ]]; then
                                # ln -s -f $DATADIR/mustshe/$PREPRO_DIR/$ref/$gender_set/$sl-$suplementl.s $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref/$gender_set/${src}-$PIVOT-${tgt}.real.pivotin.s # symbolic link
                                ln -s -f $DATADIR/mustshe/$PREPRO_DIR/$EVAL_SET/correct_ref/$gender_set/$sl-$suplementl.s $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref/$gender_set/${src}-$PIVOT-${tgt}.real.pivotin.s # symbolic link
                            fi
                        done
                    else
                        # ln -s -f $DATADIR/mustshe/$PREPRO_DIR/$ref/$gender_set/$sl-$tl.s $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref/$gender_set/${src}-$PIVOT-${tgt}.real.pivotin.s # symbolic link
                        ln -s -f $DATADIR/mustshe/$PREPRO_DIR/$EVAL_SET/correct_ref/$gender_set/$sl-$tl.s $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref/$gender_set/${src}-$PIVOT-${tgt}.real.pivotin.s # symbolic link
                    fi
                    
                    pred_src=$OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref/$gender_set/${src}-$PIVOT-${tgt}.real.pivotin.s
                    out=$OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref/$gender_set/${src}-$PIVOT-${tgt}.real.pivotin.t

                    bos='#'${tl^^}  # beginning of sentence token: target language

                    echo "Translate to $PIVOT..."
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

                    ln -s -f $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref/$gender_set/${src}-$PIVOT-${tgt}.real.pivotin.t $OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref/$gender_set/${src}-$PIVOT-${tgt}.real.pivotout.s

                    pred_src=$OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref/$gender_set/${src}-$PIVOT-${tgt}.real.pivotout.s
                    out=$OUTDIR/$MODEL/mustshe/$TRAIN_SET/pivot/$ref/$gender_set/${src}-$PIVOT-${tgt}.real.pivotout.t

                    bos='#'${tl^^}

                    echo "Translate from $PIVOT..."
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
                
                    echo '===========================================' $src $tgt 
                    # Evaluate against original reference  
                    cat $out.pt | sacrebleu $DATADIR/mustshe/raw/$ref/$gender_set/$src-$tgt.t > $out.res
                    cat $out.res
                fi
            done
        done
    done
done
