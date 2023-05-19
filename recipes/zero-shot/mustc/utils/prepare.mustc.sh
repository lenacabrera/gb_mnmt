#!/bin/bash
source ./recipes/zero-shot/config.sh

REMOVE_OVERLAP_W_MUSTSHE=$1  # true

echo "** Create 2-way MuST-C corpus"
rm -rf $DATADIR/mustc/raw/twoway
mkdir -p $DATADIR/mustc/raw/twoway
for lp_dir in $DATADIR/mustc/raw/download/*-* ; do
    lan="$(basename "$lp_dir")"
    sl=${lan:0:2}
    tl=${lan:3:2}
    if [[ "ar fa tr vi zh" != *$tl* ]]; then  # exclude languages not supported by moses tokenizer
        for set_dir in $lp_dir/*; do
            set="$(basename "$set_dir")"
            mkdir -p $DATADIR/mustc/raw/twoway/$set
            for f in $set_dir/*.*; do
                cp -f $set_dir/$set.$sl $DATADIR/mustc/raw/twoway/$set/$sl-$tl.s
                cp -f $set_dir/$set.$tl $DATADIR/mustc/raw/twoway/$set/$sl-$tl.t 
            done
        done
    fi
done

for set_dir in $DATADIR/mustc/raw/twoway/*; do
    for f in $set_dir/*\.s; do
        lan="$(basename "$f")"
        sl=${lan:0:2}
        tl=${lan:3:2}
        cp -f $f $set_dir/$tl-$sl.t
        echo $tl-$sl.t
    done
    for f in $set_dir/*\.t; do
        lan="$(basename "$f")"
        tl=${lan:0:2}
        sl=${lan:3:2}
        cp -f $f $set_dir/$sl-$tl.s
        echo $sl-$tl.s
    done
done

# rename dev -> valid
cd $DATADIR/mustc/raw/twoway
find . -depth -type d -name dev -execdir mv {} valid \;

if [[ $REMOVE_OVERLAP_W_MUSTSHE == true ]]; then
    echo "** Remove sentences overlaping with MuST-SHE data"
    bash $SCRIPTDIR/mustc/utils/remove.overlap.mustshe.mustc.sh

    # # add zero-shot directions to twoway test data
    # for set in tst-COMMON tst-HE; do
    #     set_dir=$DATADIR/mustc/raw/twoway/$set
    #     LAN="cs de es fr it nl pt ro ru"
    #     for sl in $LAN; do
    #         for tl in $LAN; do
    #             cp -f $set_dir/$sl-en.s $set_dir/$sl-$tl.s
    #             cp -f $set_dir/$sl-en.s $set_dir/$tl-$sl.t
    #         done
    #     done
    # done
fi

echo "** Create multi-way MuST-C corpus"
$SCRIPTDIR/mustc/utils/create.multiway.corpus.mustc.sh

echo "** Create twowayES MuST-C corpus"
mkdir -p $DATADIR/mustc/raw/twowayES
mkdir -p $DATADIR/mustc/raw/twowayES/train
mkdir -p $DATADIR/mustc/raw/twowayES/valid
mkdir -p $DATADIR/mustc/raw/twowayES/tst-COMMON
mkdir -p $DATADIR/mustc/raw/twowayES/tst-HE


for set_dir in train valid tst-COMMON tst-HE; do
    python3 -u $NMTDIR/utils/extract_es_par_data.py \
            $DATADIR/mustc/raw/twoway/$set_dir/en-es.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-es.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-cs.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-cs.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-de.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-de.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-fr.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-fr.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-it.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-it.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-nl.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-nl.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-pt.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-pt.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-ro.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-ro.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-ru.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-ru.t \
            $DATADIR/mustc/raw/twowayES/$set_dir/
    
        cp -f $DATADIR/mustc/raw/twoway/$set_dir/es-en.s $DATADIR/mustc/raw/twowayES/$set_dir/es-en.s
        cp -f $DATADIR/mustc/raw/twoway/$set_dir/en-es.s $DATADIR/mustc/raw/twowayES/$set_dir/en-es.s
        cp -f $DATADIR/mustc/raw/twoway/$set_dir/en-es.t $DATADIR/mustc/raw/twowayES/$set_dir/en-es.t
    for f in $DATADIR/mustc/raw/twowayES/$set_dir/*\.s; do
        lan="$(basename "$f")"
        tl=${lan:0:2}
        sl=${lan:3:2}
        cp -f $f $DATADIR/mustc/raw/twowayES/$set_dir/$sl-$tl.t
    done
done

echo "** Create twowayDE MuST-C corpus"
mkdir -p $DATADIR/mustc/raw/twowayDE
mkdir -p $DATADIR/mustc/raw/twowayDE/train
mkdir -p $DATADIR/mustc/raw/twowayDE/valid
mkdir -p $DATADIR/mustc/raw/twowayDE/tst-COMMON
mkdir -p $DATADIR/mustc/raw/twowayDE/tst-HE


for set_dir in train valid tst-COMMON tst-HE; do
    python3 -u $NMTDIR/utils/extract_de_par_data.py \
            $DATADIR/mustc/raw/twoway/$set_dir/en-de.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-de.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-cs.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-cs.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-es.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-es.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-fr.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-fr.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-it.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-it.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-nl.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-nl.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-pt.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-pt.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-ro.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-ro.t \
            $DATADIR/mustc/raw/twoway/$set_dir/en-ru.s \
            $DATADIR/mustc/raw/twoway/$set_dir/en-ru.t \
            $DATADIR/mustc/raw/twowayDE/$set_dir/
    
        cp -f $DATADIR/mustc/raw/twoway/$set_dir/de-en.s $DATADIR/mustc/raw/twowayDE/$set_dir/de-en.s
        cp -f $DATADIR/mustc/raw/twoway/$set_dir/en-de.s $DATADIR/mustc/raw/twowayDE/$set_dir/en-de.s
        cp -f $DATADIR/mustc/raw/twoway/$set_dir/en-de.t $DATADIR/mustc/raw/twowayDE/$set_dir/en-de.t
    for f in $DATADIR/mustc/raw/twowayDE/$set_dir/*\.s; do
        lan="$(basename "$f")"
        tl=${lan:0:2}
        sl=${lan:3:2}
        cp -f $f $DATADIR/mustc/raw/twowayDE/$set_dir/$sl-$tl.t
    done
done