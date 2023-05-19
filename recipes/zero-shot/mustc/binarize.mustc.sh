model_name=transformer
prepro_name=mustc/prepro_20000_subwordnmt
nway=multiwayES  # twoway, multiway, multiwayDE, multiwayESFRIT

if [ $nway == twoway ]; then
echo twoway
    # english
    S_LAN="cs|de|en|en|en|en|en|en|en|en|en|es|fr|it|nl|pt|ro|ru" # has to be sorted alphabetically
    T_LAN="en|en|cs|de|es|fr|it|nl|pt|ro|ru|en|en|en|en|en|en|en"
elif [ $nway == multiwayEN ]; then
echo twoway
    # english
    S_LAN="cs|de|en|en|en|en|en|en|en|en|en|es|fr|it|nl|pt|ro|ru" # has to be sorted alphabetically
    T_LAN="en|en|cs|de|es|fr|it|nl|pt|ro|ru|en|en|en|en|en|en|en"
elif [[ $nway == multiwayES ]]; then
echo ES
    # spanish
    S_LAN="cs|de|en|es|es|es|es|es|es|es|es|es|fr|it|nl|pt|ro|ru" # has to be sorted alphabetically
    T_LAN="es|es|es|cs|de|en|fr|it|nl|pt|ro|ru|es|es|es|es|es|es"
elif [[ $nway == twowayES ]]; then
echo ES
    # spanish
    S_LAN="cs|de|en|es|es|es|es|es|es|es|es|es|fr|it|nl|pt|ro|ru" # has to be sorted alphabetically
    T_LAN="es|es|es|cs|de|en|fr|it|nl|pt|ro|ru|es|es|es|es|es|es"
elif [ $nway == multiwayFR ]; then
echo FR
    # french
    S_LAN="cs|de|en|es|fr|fr|fr|fr|fr|fr|fr|fr|fr|it|nl|pt|ro|ru" # has to be sorted alphabetically
    T_LAN="fr|fr|fr|fr|cs|de|en|es|it|nl|pt|ro|ru|fr|fr|fr|fr|fr"
elif [ $nway == multiwayESFRIT ]; then
echo ESFRIT
    # spanisch, italian, french
    S_LAN="cs|cs|cs|de|de|de|en|en|en|es|es|es|es|es|es|es|es|es|fr|fr|fr|fr|fr|fr|fr|fr|fr|it|it|it|it|it|it|it|it|it|nl|nl|nl|pt|pt|pt|ro|ro|ro|ru|ru|ru" # has to be sorted alphabetically
    T_LAN="es|fr|it|es|fr|it|es|fr|it|cs|de|en|fr|it|nl|pt|ro|ru|cs|de|en|es|it|nl|pt|ro|ru|cs|de|en|es|fr|nl|pt|ro|ru|es|fr|it|es|fr|it|es|fr|it|es|fr|it"
elif [ $nway == twowayDE ]; then
echo DE
    # german
    S_LAN="cs|de|de|de|de|de|de|de|de|de|en|es|fr|it|nl|pt|ro|ru" # has to be sorted alphabetically
    T_LAN="de|cs|en|es|fr|it|nl|pt|ro|ru|de|de|de|de|de|de|de|de"
elif [ $nway == multiwayDE ]; then
echo DE
    # german
    S_LAN="cs|de|de|de|de|de|de|de|de|de|en|es|fr|it|nl|pt|ro|ru" # has to be sorted alphabetically
    T_LAN="de|cs|en|es|fr|it|nl|pt|ro|ru|de|de|de|de|de|de|de|de"
# else 
#     # multiway
#     S_LAN="cs|cs|cs|cs|cs|cs|cs|cs|cs|de|de|de|de|de|de|de|de|de|en|en|en|en|en|en|en|en|en|es|es|es|es|es|es|es|es|es|fr|fr|fr|fr|fr|fr|fr|fr|fr|it|it|it|it|it|it|it|it|it|nl|nl|nl|nl|nl|nl|nl|nl|nl|pt|pt|pt|pt|pt|pt|pt|pt|pt|ro|ro|ro|ro|ro|ro|ro|ro|ro|ru|ru|ru|ru|ru|ru|ru|ru|ru" # has to be sorted alphabetically
#     T_LAN="de|en|es|fr|it|nl|pt|ro|ru|cs|en|es|fr|it|nl|pt|ro|ru|cs|de|es|fr|it|nl|pt|ro|ru|cs|de|en|fr|it|nl|pt|ro|ru|cs|de|en|es|it|nl|pt|ro|ru|cs|de|en|es|fr|nl|pt|ro|ru|cs|de|en|es|fr|it|pt|ro|ru|cs|de|en|es|fr|it|nl|ro|ru|cs|de|en|es|fr|it|nl|pt|ru|cs|de|en|es|fr|it|nl|pt|ro"
fi

IFS='|' read -r -a arrayS <<< $S_LAN
IFS='|' read -r -a arrayT <<< $T_LAN

BASEDIR=$WORKDIR
echo $BASEDIR

rm -rf $DATADIR/$prepro_name/$nway/tmp/${model_name}
mkdir -p $DATADIR/$prepro_name/$nway/tmp/${model_name}.$prepro_name/$nway

datadir=$DATADIR/$prepro_name/$nway/binarized_mmem/train
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
            echo -n "" > $DATADIR/$prepro_name/$nway/tmp/${model_name}.$prepro_name/$nway/$set-$pair.$l

            for f in $DATADIR/${prepro_name}/$nway/$set/$pair*\.${l}
            do  # write out to tmp folder
                    cat $f >> $DATADIR/$prepro_name/$nway/tmp/${model_name}.$prepro_name/$nway/$set-$pair.$l
            done
        done
    done
done

# concat with "|" as delimitter
function join_by { local IFS="$1"; shift; echo "$*"; }

echo $DATADIR/$prepro_name/$nway/tmp/${model_name}/train

python3 $NMTDIR/preprocess.py \
       -train_src `join_by '|' $DATADIR/$prepro_name/$nway/tmp/${model_name}.$prepro_name/$nway/train*\.s` \
       -train_tgt `join_by '|' $DATADIR/$prepro_name/$nway/tmp/${model_name}.$prepro_name/$nway/train*\.t` \
       -valid_src `join_by '|' $DATADIR/$prepro_name/$nway/tmp/${model_name}.$prepro_name/$nway/valid*\.s` \
       -valid_tgt `join_by '|' $DATADIR/$prepro_name/$nway/tmp/${model_name}.$prepro_name/$nway/valid*\.t` \
       -train_src_lang $S_LAN \
       -train_tgt_lang $T_LAN \
       -valid_src_lang $S_LAN \
       -valid_tgt_lang $T_LAN \
       -save_data $datadir \
       -src_seq_length 512 \
       -tgt_seq_length 512 \
       -join_vocab \
       -no_bos \
       -num_threads 16 \
       -format mmem
        
