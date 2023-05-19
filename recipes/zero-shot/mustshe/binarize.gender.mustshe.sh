model_name=transformer
TRAIN_SET=twoway
prepro_name=mustshe/prepro_20000_subwordnmt/$TRAIN_SET.GEN

S_LAN_MUSTC="cs|de|en|es|fr|it|nl|pt|ro|ru"
T_LAN_MUSTC="cs|de|en|es|fr|it|nl|pt|ro|ru"

# S_LAN="es|es|es|fr|fr|fr|it|it|it" # has to be sorted alphabetically
# T_LAN="en|fr|it|en|es|it|en|es|fr"

S_LAN="es|fr|it" # has to be sorted alphabetically
T_LAN="en|en|en"

IFS='|' read -r -a arrayS <<< $S_LAN
IFS='|' read -r -a arrayT <<< $T_LAN

BASEDIR=$WORKDIR
echo $BASEDIR

rm -rf $DATADIR/$prepro_name/tmp/${model_name}
mkdir -p $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/
mkdir -p $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/label
mkdir -p $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/label/sent
mkdir -p $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/label/tok

datadir=$DATADIR/$prepro_name/binarized_mmem/train
mkdir $datadir -p

# for each language pair, e.g. (hi, en), (ne, en)
for l in s t
do
    for set in train valid
    do
        # loop through language pairs
        for index in "${!arrayS[@]}"  #pair in te-en ta-en #ne-en si-en
        do
            pair="${arrayS[index]}-${arrayT[index]}"
            echo -n "" > $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/$set-$pair.$l

            for f in $DATADIR/${prepro_name}/$set/$pair*\.${l}
            do  # write out to tmp folder
                    cat $f >> $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/$set-$pair.$l
            done

            for f in $DATADIR/${prepro_name}/$set/label/sent/*\.s
            do  # write out to tmp folder
                lan="$(basename "$f")"
                sl=${lan:0:2} 
                # cat $f >> $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/label/$set-label-$sl.s
                cp $f $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/label/sent/$set-$sl.s
            done

            for f in $DATADIR/${prepro_name}/$set/label/tok/*\.s
            do  # write out to tmp folder
                lan="$(basename "$f")"
                sl=${lan:0:2} 
                # cat $f >> $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/label/$set-label-$sl.s
                cp $f $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/label/tok/$set-$sl.s
            done

        done
    done
done

# concat with "|" as delimitter
function join_by { local IFS="$1"; shift; echo "$*"; }

# echo $DATADIR/$prepro_name/tmp/${model_name}/train
echo `join_by '|' $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/train*\.s`

python3 $NMTDIR/preprocess_mustshe.py \
       -train_src `join_by '|' $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/train*\.s` \
       -train_tgt `join_by '|' $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/train*\.t` \
       -valid_src `join_by '|' $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/valid*\.s` \
       -valid_tgt `join_by '|' $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/valid*\.t` \
       -train_src_lang $S_LAN \
       -train_tgt_lang $T_LAN \
       -valid_src_lang $S_LAN \
       -valid_tgt_lang $T_LAN \
       -train_sent_label `join_by '|' $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/label/sent/train*\.s` \
       -valid_sent_label `join_by '|' $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/label/sent/valid*\.s` \
       -train_tok_label `join_by '|' $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/label/tok/train*\.s` \
       -valid_tok_label `join_by '|' $DATADIR/$prepro_name/tmp/${model_name}.$prepro_name/label/tok/valid*\.s` \
       -save_data $datadir \
       -src_seq_length 512 \
       -tgt_seq_length 512 \
       -join_vocab \
       -no_bos \
       -num_threads 16 \
       -format mmem
        
