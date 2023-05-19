#!/bin/bash
source ./recipes/zero-shot/config.sh

export MODEL=$1

mkdir $DATADIR/$MODEL/pivot -p
mkdir $OUTDIR/$MODEL/pivot -p

# IWSLT languages
langs="ro it nl"

for src in $langs; do
    for tgt in $langs; do
        if [ $src != $tgt ]; then
        
            echo $src " -> en -> " $tgt

            # (1) pivot into English
            export sl=$src
            export tl=en

            # ln -s -f $DATADIR/iwslt17_multiway/prepro_20000_subwordnmt/test/$sl-$tl.s  $OUTDIR/$MODEL/pivot/tst2017${src}-en-${tgt}.real.pivotin.s # symbolic link
            # above line is correct, however, files are not truly parallel; thus, use below
            ln -s -f $DATADIR/iwslt17_multiway/prepro_20000_subwordnmt/test/$sl-$tgt.s  $OUTDIR/$MODEL/pivot/tst2017${src}-en-${tgt}.real.pivotin.s 
            
            pred_src=$OUTDIR/$MODEL/pivot/tst2017${src}-en-${tgt}.real.pivotin.s
            out=$OUTDIR/$MODEL/pivot/tst2017${src}-en-${tgt}.real.pivotin.t

            bos='#'${tl^^}

            echo "Translate to EN..."
            python3 -u $NMTDIR/translate.py \
                    -gpu $GPU \
                    -model $WORKDIR/model/$MODEL/model.pt \
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
            export sl=en
            export tl=$tgt

            ln -s -f $OUTDIR/$MODEL/pivot/tst2017${src}-en-${tgt}.real.pivotin.t $OUTDIR/$MODEL/pivot/tst2017${src}-en-${tgt}.real.pivotout.s

            pred_src=$OUTDIR/$MODEL/pivot/tst2017${src}-en-${tgt}.real.pivotout.s
            out=$OUTDIR/$MODEL/pivot/tst2017${src}-en-${tgt}.real.pivotout.t

            bos='#'${tl^^}

            echo "Translate from EN..."
            python3 -u $NMTDIR/translate.py \
                    -gpu $GPU \
                    -model $WORKDIR/model/$MODEL/model.pt \
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
            cat $out.pt | sacrebleu $DATADIR/iwslt17_multiway/raw/test/tst2017$tgt-$src.$tgt > $out.res
            cat $out.res
        fi
    done
done

