#!/bin/bash

if [ -z "$BASEDIR" ]; then
    BASEDIR=/
fi

if [ -z "$MOSESDIR" ]; then
    MOSESDIR=/opt/mosesdecoder/
fi

if [ -z "$BPEDIR" ]; then
    BPEDIR=/opt/subword-nmt/
fi

if [ -z "$BPESIZE" ]; then
    BPESIZE=40000
fi

if [ -z "$SRC_INDIC" ]; then
    SRC_INDIC=false
fi

if [ -z "$PARA" ]; then
    PARA=parallel	
fi


input=$1 	# systemName
name=$2 	# $PREPRO_DIR

BASEDIR=$WORKDIR/data/$input

mkdir -p $BASEDIR/tmp/${name}/tok/train
mkdir -p $BASEDIR/tmp/${name}/tok/valid
mkdir -p $BASEDIR/tmp/${name}/sc/train
mkdir -p $BASEDIR/tmp/${name}/sc/valid
mkdir -p $WORKDIR/model/${name}
mkdir -p $WORKDIR/model/${name}/${input}
mkdir -p $BASEDIR/${name}/train
mkdir -p $BASEDIR/${name}/valid

echo "codec: " $WORKDIR/model/${name}/${input}/codec


### (1) TOKENIZATION 
echo "*** Tokenization" 

## Source
echo "" > $BASEDIR/tmp/${name}/corpus.tok.s

# Train
for f in $BASEDIR/raw/train/*\.s
    do
    lan_pair="$(basename "$f")"
    sl=${lan_pair:0:2}
    if [ "$sl" != 'ml' ] && [ "$sl" != 'te' ]  && [ "$sl" != 'kn' ] && [ "$sl" != 'ta' ] && [ "$sl" != 'bn' ] && [ "$sl" != 'gu' ] && [ "$sl" != 'hi' ] && [ "$sl" != 'mr' ] && [ "$sl" != 'or' ] && [ "$sl" != 'pa' ]; then
        cat $f | perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${sl} > $BASEDIR/tmp/${name}/tok/train/${f##*/}
    else
        echo '*** Using indic tokenizer for src' $f
        $INDIC_TOKENIZER ${sl} $f > $BASEDIR/tmp/${name}/tok/train/${f##*/}
    fi
    cat $BASEDIR/tmp/${name}/tok/train/${f##*/} >> $BASEDIR/tmp/${name}/corpus.tok.s
done
# Valid
for f in $BASEDIR/raw/valid/*\.s
    do
    lan_pair="$(basename "$f")"
    sl=${lan_pair:0:2}
    if [ "$sl" != 'ml' ] && [ "$sl" != 'te' ]  && [ "$sl" != 'kn' ] && [ "$sl" != 'ta' ] && [ "$sl" != 'bn' ] && [ "$sl" != 'gu' ] && [ "$sl" != 'hi' ] && [ "$sl" != 'mr' ] && [ "$sl" != 'or' ] && [ "$sl" != 'pa' ]; then
        cat $f | perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${sl} > $BASEDIR/tmp/${name}/tok/valid/${f##*/}
    else
        echo '*** Using indic tokenizer for src' $f
        $INDIC_TOKENIZER ${sl} $f > $BASEDIR/tmp/${name}/tok/valid/${f##*/}
    fi
done

## Target
echo "" > $BASEDIR/tmp/${name}/corpus.tok.t

# Train
for f in $BASEDIR/raw/train/*\.t
    do
    lan_pair="$(basename "$f")"
    tl=${lan_pair:3:2}
    if [ "$tl" != 'ml' ] && [ "$tl" != 'te' ]  && [ "$tl" != 'kn' ] && [ "$tl" != 'ta' ] && [ "$tl" != 'bn' ] && [ "$tl" != 'gu' ] && [ "$tl" != 'hi' ] && [ "$tl" != 'mr' ] && [ "$tl" != 'or' ] && [ "$tl" != 'pa' ]; then
        cat $f | perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${tl} > $BASEDIR/tmp/${name}/tok/train/${f##*/}
    else
        echo '*** Using indic tokenizer for tgt' $f
        $INDIC_TOKENIZER ${tl} $f > $BASEDIR/tmp/${name}/tok/train/${f##*/}
    fi
    cat $BASEDIR/tmp/${name}/tok/train/${f##*/} >> $BASEDIR/tmp/${name}/corpus.tok.t
done

# Valid
for f in $BASEDIR/raw/valid/*\.t
    do
    lan_pair="$(basename "$f")"
    tl=${lan_pair:3:2}
    if [ "$tl" != 'ml' ] && [ "$tl" != 'te' ]  && [ "$tl" != 'kn' ] && [ "$tl" != 'ta' ] && [ "$tl" != 'bn' ] && [ "$tl" != 'gu' ] && [ "$tl" != 'hi' ] && [ "$tl" != 'mr' ] && [ "$tl" != 'or' ] && [ "$tl" != 'pa' ]; then
        cat $f | perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${tl} > $BASEDIR/tmp/${name}/tok/valid/${f##*/}
    else
        echo '*** Using indic tokenizer for tgt' $f
            $INDIC_TOKENIZER ${tl} $f > $BASEDIR/tmp/${name}/tok/valid/${f##*/}
    fi
done

### (2) SMARTCASE
echo "*** Learning Truecaser" 

## Source
if [ "$SRC_INDIC" != true ]; then
    # train
    $MOSESDIR/scripts/recaser/train-truecaser.perl --model $WORKDIR/model/${name}/${input}/truecase-model.s --corpus $BASEDIR/tmp/${name}/corpus.tok.s
    # apply
    for set in valid train
        do
            for f in $BASEDIR/tmp/${name}/tok/$set/*\.s
                do
                cat $f | $MOSESDIR/scripts/recaser/truecase.perl --model $WORKDIR/model/${name}/${input}/truecase-model.s > $BASEDIR/tmp/${name}/sc/$set/${f##*/}
        done
    done
else # skip smartcasing
    for set in valid train
        do
        for f in $BASEDIR/tmp/${name}/tok/$set/*\.s
            do
            cat $f > $BASEDIR/tmp/${name}/sc/$set/${f##*/}
        done
    done
fi

echo "" > $BASEDIR/tmp/${name}/corpus.sc.s
for f in $BASEDIR/tmp/${name}/sc/train/*\.s
    do
    cat $f >> $BASEDIR/tmp/${name}/corpus.sc.s
done

## Target
# train
$MOSESDIR/scripts/recaser/train-truecaser.perl --model $WORKDIR/model/${name}/${input}/truecase-model.t --corpus $BASEDIR/tmp/${name}/corpus.tok.t
# apply
for set in valid train
    do
    for f in $BASEDIR/tmp/${name}/tok/$set/*\.t
        do
        cat $f | $MOSESDIR/scripts/recaser/truecase.perl --model $WORKDIR/model/${name}/${input}/truecase-model.t > $BASEDIR/tmp/${name}/sc/$set/${f##*/}
    done
done

echo "" > $BASEDIR/tmp/${name}/corpus.sc.t
for f in $BASEDIR/tmp/${name}/sc/train/*\.t
do
cat $f >> $BASEDIR/tmp/${name}/corpus.sc.t
done

### (3) BPE
echo "*** Learning BPE of size" $BPESIZE
if [ ! "$SENTENCE_PIECE" == true ]; then
    # using subword-nmt 
	echo "*** BPE by subword-nmt"
	$BPEDIR/subword_nmt/learn_joint_bpe_and_vocab.py --input $BASEDIR/tmp/${name}/corpus.sc.s $BASEDIR/tmp/${name}/corpus.sc.t -s $BPESIZE -o $WORKDIR/model/${name}/${input}/codec --write-vocabulary $WORKDIR/model/${name}/${input}/voc.s $WORKDIR/model/${name}/${input}/voc.t

    ## Source
	for set in valid train
	    do
		for f in $BASEDIR/tmp/${name}/sc/$set/*\.s
            do
            echo $f
            $BPEDIR/subword_nmt/apply_bpe.py -c $WORKDIR/model/${name}/${input}/codec --vocabulary $WORKDIR/model/${name}/${input}/voc.s --vocabulary-threshold 50 < $f > $BASEDIR/${name}/$set/${f##*/}
		done
	done

    ## Target
	for set in valid train
	    do
		for f in $BASEDIR/tmp/${name}/sc/$set/*\.t
            do
            echo $f
            $BPEDIR/subword_nmt/apply_bpe.py -c $WORKDIR/model/${name}/${input}/codec --vocabulary $WORKDIR/model/${name}/${input}/voc.t --vocabulary-threshold 50 < $f > $BASEDIR/${name}/$set/${f##*/}
		done
	done

else
    # using SentencePiece
	echo "*** BPE by sentencepiece"
	spm_train \
	--input=$BASEDIR/tmp/${name}/corpus.sc.s,$BASEDIR/tmp/${name}/corpus.sc.t \
        --model_prefix=$BASEDIR/${name}/sentencepiece.bpe \
        --vocab_size=$BPESIZE \
        --character_coverage=1.0 \
        --model_type=bpe
	for set in valid train
	    do
		for f in $BASEDIR/tmp/${name}/sc/$set/* #\.s
		do
		echo $f
		spm_encode \
        	--model=$BASEDIR/${name}/sentencepiece.bpe.model \
        	--output_format=piece \
		--vocabulary_threshold 50 < $f > $BASEDIR/${name}/$set/${f##*/}
		done
	done
fi

rm -r $BASEDIR/tmp
