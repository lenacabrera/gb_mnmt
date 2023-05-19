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


input=$1 	    # systemName
prepro_name=$2 	# $PREPRO_DIR
nway=$3

BASEDIR=$DATADIR/$input/raw/$nway

mkdir -p $BASEDIR/tmp/${prepro_name}/tok/train
mkdir -p $BASEDIR/tmp/${prepro_name}/tok/valid
mkdir -p $BASEDIR/tmp/${prepro_name}/sc/train
mkdir -p $BASEDIR/tmp/${prepro_name}/sc/valid
mkdir -p $WORKDIR/model/${prepro_name}
mkdir -p $WORKDIR/model/${prepro_name}/${input}
mkdir -p $WORKDIR/model/${prepro_name}/${input}/${nway}
mkdir -p $DATADIR/$input/${prepro_name}/$nway/
mkdir -p $DATADIR/$input/${prepro_name}/$nway/train
mkdir -p $DATADIR/$input/${prepro_name}/$nway/valid


### (1) TOKENIZATION 
echo "*** Tokenization" 

## Source
echo "" > $BASEDIR/tmp/${prepro_name}/corpus.tok.s

# Train
for f in $BASEDIR/train/*\.s; do
    lan_pair="$(basename "$f")"
    sl=${lan_pair:0:2}
    cat $f | perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${sl} > $BASEDIR/tmp/${prepro_name}/tok/train/${f##*/}
    cat $BASEDIR/tmp/${prepro_name}/tok/train/${f##*/} >> $BASEDIR/tmp/${prepro_name}/corpus.tok.s
done
# Valid
for f in $BASEDIR/valid/*\.s; do
    lan_pair="$(basename "$f")"
    sl=${lan_pair:0:2}
    cat $f | perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${sl} > $BASEDIR/tmp/${prepro_name}/tok/valid/${f##*/}
done

## Target
echo "" > $BASEDIR/tmp/${prepro_name}/corpus.tok.t

# Train
for f in $BASEDIR/train/*\.t; do
    lan_pair="$(basename "$f")"
    tl=${lan_pair:3:2}
    cat $f | perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${tl} > $BASEDIR/tmp/${prepro_name}/tok/train/${f##*/}
    cat $BASEDIR/tmp/${prepro_name}/tok/train/${f##*/} >> $BASEDIR/tmp/${prepro_name}/corpus.tok.t
done

# Valid
for f in $BASEDIR/valid/*\.t; do
    lan_pair="$(basename "$f")"
    tl=${lan_pair:3:2}
    cat $f | perl $MOSESDIR/scripts/tokenizer/tokenizer.perl -l ${tl} > $BASEDIR/tmp/${prepro_name}/tok/valid/${f##*/}
done

### (2) SMARTCASE
echo "*** Learning Truecaser" 

## Source
# train
$MOSESDIR/scripts/recaser/train-truecaser.perl --model $WORKDIR/model/${prepro_name}/${input}/${nway}/truecase-model.s --corpus $BASEDIR/tmp/${prepro_name}/corpus.tok.s
# apply
for set in valid train; do
        for f in $BASEDIR/tmp/${prepro_name}/tok/$set/*\.s; do
            cat $f | $MOSESDIR/scripts/recaser/truecase.perl --model $WORKDIR/model/${prepro_name}/${input}/${nway}/truecase-model.s > $BASEDIR/tmp/${prepro_name}/sc/$set/${f##*/}
    done
done

echo "" > $BASEDIR/tmp/${prepro_name}/corpus.sc.s
for f in $BASEDIR/tmp/${prepro_name}/sc/train/*\.s; do
    cat $f >> $BASEDIR/tmp/${prepro_name}/corpus.sc.s
done

## Target
# train
$MOSESDIR/scripts/recaser/train-truecaser.perl --model $WORKDIR/model/${prepro_name}/${input}/${nway}/truecase-model.t --corpus $BASEDIR/tmp/${prepro_name}/corpus.tok.t
# apply
for set in valid train; do
    for f in $BASEDIR/tmp/${prepro_name}/tok/$set/*\.t; do
        cat $f | $MOSESDIR/scripts/recaser/truecase.perl --model $WORKDIR/model/${prepro_name}/${input}/${nway}/truecase-model.t > $BASEDIR/tmp/${prepro_name}/sc/$set/${f##*/}
    done
done

echo "" > $BASEDIR/tmp/${prepro_name}/corpus.sc.t
for f in $BASEDIR/tmp/${prepro_name}/sc/train/*\.t; do
    cat $f >> $BASEDIR/tmp/${prepro_name}/corpus.sc.t
done

### (3) BPE
echo "*** Learning BPE of size" $BPESIZE
if [ ! "$SENTENCE_PIECE" == true ]; then
    # using subword-nmt 
	echo "*** BPE by subword-nmt"
	$BPEDIR/subword_nmt/learn_joint_bpe_and_vocab.py --input $BASEDIR/tmp/${prepro_name}/corpus.sc.s $BASEDIR/tmp/${prepro_name}/corpus.sc.t -s $BPESIZE -o $WORKDIR/model/${prepro_name}/${input}/${nway}/codec --write-vocabulary $WORKDIR/model/${prepro_name}/${input}/${nway}/voc.s $WORKDIR/model/${prepro_name}/${input}/${nway}/voc.t

    ## Source
	for set in valid train; do
		for f in $BASEDIR/tmp/${prepro_name}/sc/$set/*\.s; do
            echo $f
            $BPEDIR/subword_nmt/apply_bpe.py -c $WORKDIR/model/${prepro_name}/${input}/${nway}/codec --vocabulary $WORKDIR/model/${prepro_name}/${input}/${nway}/voc.s --vocabulary-threshold 50 < $f > $DATADIR/$input/${prepro_name}/$nway/$set/${f##*/}
		done
	done

    ## Target
	for set in valid train; do
		for f in $BASEDIR/tmp/${prepro_name}/sc/$set/*\.t; do
            echo $f
            $BPEDIR/subword_nmt/apply_bpe.py -c $WORKDIR/model/${prepro_name}/${input}/${nway}/codec --vocabulary $WORKDIR/model/${prepro_name}/${input}/${nway}/voc.t --vocabulary-threshold 50 < $f > $DATADIR/$input/${prepro_name}/$nway/$set/${f##*/}
		done
	done

else
    # using SentencePiece
	echo "*** BPE by sentencepiece"
	spm_train \
	--input=$BASEDIR/tmp/${prepro_name}/corpus.sc.s,$BASEDIR/tmp/${prepro_name}/corpus.sc.t \
        --model_prefix=$DATADIR/$input/${prepro_name}/$nway/sentencepiece.bpe \
        --vocab_size=$BPESIZE \
        --character_coverage=1.0 \
        --model_type=bpe
	for set in valid train; do
		for f in $BASEDIR/tmp/${prepro_name}/sc/$set/*; do
		echo $f
		spm_encode \
        	--model=$DATADIR/$input/${prepro_name}/$nway/sentencepiece.bpe.model \
        	--output_format=piece \
		--vocabulary_threshold 50 < $f > $DATADIR/$input/${prepro_name}/$nway/$set/${f##*/}
		done
	done
fi

# rm -r $BASEDIR/tmp
