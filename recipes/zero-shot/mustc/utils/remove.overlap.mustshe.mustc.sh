
python3 -u $NMTDIR/utils/prepro_tsv_mustshe.py $DATADIR/mustshe/raw/ correct_ref wrong_ref

mkdir -p $DATADIR/mustc/raw/twoway/novlp
mkdir -p $DATADIR/mustc/raw/twoway/novlp/train
mkdir -p $DATADIR/mustc/raw/twoway/novlp/valid

echo "====== Remove overlap with MuST-SHE from MuST-C training data"
python -u $NMTDIR/utils/remove_overlap_w_mustshe_f_mustc.py \
    $DATADIR/mustc/raw/twoway/train/en-cs.s \
    $DATADIR/mustc/raw/twoway/train/en-de.s \
    $DATADIR/mustc/raw/twoway/train/en-es.s \
    $DATADIR/mustc/raw/twoway/train/en-fr.s \
    $DATADIR/mustc/raw/twoway/train/en-it.s \
    $DATADIR/mustc/raw/twoway/train/en-nl.s \
    $DATADIR/mustc/raw/twoway/train/en-pt.s \
    $DATADIR/mustc/raw/twoway/train/en-ro.s \
    $DATADIR/mustc/raw/twoway/train/en-ru.s \
    $DATADIR/mustc/raw/twoway/train/cs-en.s \
    $DATADIR/mustc/raw/twoway/train/de-en.s \
    $DATADIR/mustc/raw/twoway/train/es-en.s \
    $DATADIR/mustc/raw/twoway/train/fr-en.s \
    $DATADIR/mustc/raw/twoway/train/it-en.s \
    $DATADIR/mustc/raw/twoway/train/nl-en.s \
    $DATADIR/mustc/raw/twoway/train/pt-en.s \
    $DATADIR/mustc/raw/twoway/train/ro-en.s \
    $DATADIR/mustc/raw/twoway/train/ru-en.s \
    $DATADIR/mustshe/raw/correct_ref/en_par.s \
    $DATADIR/mustc/raw/twoway/novlp/train/

echo "====== Remove overlap with MuST-SHE from MuST-C validation data"
python -u $NMTDIR/utils/remove_overlap_w_mustshe_f_mustc.py \
    $DATADIR/mustc/raw/twoway/valid/en-cs.s \
    $DATADIR/mustc/raw/twoway/valid/en-de.s \
    $DATADIR/mustc/raw/twoway/valid/en-es.s \
    $DATADIR/mustc/raw/twoway/valid/en-fr.s \
    $DATADIR/mustc/raw/twoway/valid/en-it.s \
    $DATADIR/mustc/raw/twoway/valid/en-nl.s \
    $DATADIR/mustc/raw/twoway/valid/en-pt.s \
    $DATADIR/mustc/raw/twoway/valid/en-ro.s \
    $DATADIR/mustc/raw/twoway/valid/en-ru.s \
    $DATADIR/mustc/raw/twoway/valid/cs-en.s \
    $DATADIR/mustc/raw/twoway/valid/de-en.s \
    $DATADIR/mustc/raw/twoway/valid/es-en.s \
    $DATADIR/mustc/raw/twoway/valid/fr-en.s \
    $DATADIR/mustc/raw/twoway/valid/it-en.s \
    $DATADIR/mustc/raw/twoway/valid/nl-en.s \
    $DATADIR/mustc/raw/twoway/valid/pt-en.s \
    $DATADIR/mustc/raw/twoway/valid/ro-en.s \
    $DATADIR/mustc/raw/twoway/valid/ru-en.s \
    $DATADIR/mustshe/raw/correct_ref/en_par.s \
    $DATADIR/mustc/raw/twoway/novlp/valid/


rm -f $DATADIR/mustc/raw/twoway/train/.\*
rm -f $DATADIR/mustc/raw/twoway/valid/.\*

mv $DATADIR/mustc/raw/twoway/novlp/train/* $DATADIR/mustc/raw/twoway/train
mv $DATADIR/mustc/raw/twoway/novlp/valid/* $DATADIR/mustc/raw/twoway/valid

rm -r $DATADIR/mustc/raw/twoway/novlp/