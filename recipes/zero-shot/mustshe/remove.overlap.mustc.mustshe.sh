mkdir -p $DATADIR/mustshe/raw/correct_ref/tmp
mkdir -p $DATADIR/mustshe/raw/wrong_ref/tmp

echo "====== Remove overlap with MuST-C training data"
python -u $NMTDIR/utils/remove_overlap_w_mustc_f_mustshe.py \
    $DATADIR/mustc/raw/twoway/train/en-cs.s \
    $DATADIR/mustc/raw/twoway/train/en-de.s \
    $DATADIR/mustc/raw/twoway/train/en-es.s \
    $DATADIR/mustc/raw/twoway/train/en-fr.s \
    $DATADIR/mustc/raw/twoway/train/en-it.s \
    $DATADIR/mustc/raw/twoway/train/en-nl.s \
    $DATADIR/mustc/raw/twoway/train/en-pt.s \
    $DATADIR/mustc/raw/twoway/train/en-ro.s \
    $DATADIR/mustc/raw/twoway/train/en-ru.s \
    $DATADIR/mustshe/raw/correct_ref/en_par.s \
    $DATADIR/mustshe/raw/correct_ref/es_par.s \
    $DATADIR/mustshe/raw/correct_ref/fr_par.s \
    $DATADIR/mustshe/raw/correct_ref/it_par.s \
    $DATADIR/mustshe/raw/correct_ref/es_speaker.csv \
    $DATADIR/mustshe/raw/correct_ref/es_category.csv \
    $DATADIR/mustshe/raw/correct_ref/es_gterms.csv \
    $DATADIR/mustshe/raw/correct_ref/fr_speaker.csv \
    $DATADIR/mustshe/raw/correct_ref/fr_category.csv \
    $DATADIR/mustshe/raw/correct_ref/fr_gterms.csv \
    $DATADIR/mustshe/raw/correct_ref/it_speaker.csv \
    $DATADIR/mustshe/raw/correct_ref/it_category.csv \
    $DATADIR/mustshe/raw/correct_ref/it_gterms.csv \
    $DATADIR/mustshe/raw/wrong_ref/es_par.s \
    $DATADIR/mustshe/raw/wrong_ref/fr_par.s \
    $DATADIR/mustshe/raw/wrong_ref/it_par.s \
    $DATADIR/mustshe/raw/wrong_ref/es_speaker.csv \
    $DATADIR/mustshe/raw/wrong_ref/es_category.csv \
    $DATADIR/mustshe/raw/wrong_ref/es_gterms.csv \
    $DATADIR/mustshe/raw/wrong_ref/fr_speaker.csv \
    $DATADIR/mustshe/raw/wrong_ref/fr_category.csv \
    $DATADIR/mustshe/raw/wrong_ref/fr_gterms.csv \
    $DATADIR/mustshe/raw/wrong_ref/it_speaker.csv \
    $DATADIR/mustshe/raw/wrong_ref/it_category.csv \
    $DATADIR/mustshe/raw/wrong_ref/it_gterms.csv \
    $DATADIR/mustshe/raw/correct_ref/tmp/ \
    $DATADIR/mustshe/raw/wrong_ref/tmp/

echo "====== Remove overlap with MuST-C validation data"
python -u $NMTDIR/utils/remove_overlap_w_mustc_f_mustshe.py \
    $DATADIR/mustc/raw/twoway/valid/en-cs.s \
    $DATADIR/mustc/raw/twoway/valid/en-de.s \
    $DATADIR/mustc/raw/twoway/valid/en-es.s \
    $DATADIR/mustc/raw/twoway/valid/en-fr.s \
    $DATADIR/mustc/raw/twoway/valid/en-it.s \
    $DATADIR/mustc/raw/twoway/valid/en-nl.s \
    $DATADIR/mustc/raw/twoway/valid/en-pt.s \
    $DATADIR/mustc/raw/twoway/valid/en-ro.s \
    $DATADIR/mustc/raw/twoway/valid/en-ru.s \
    $DATADIR/mustshe/raw/correct_ref/tmp/en_par.s \
    $DATADIR/mustshe/raw/correct_ref/tmp/es_par.s \
    $DATADIR/mustshe/raw/correct_ref/tmp/fr_par.s \
    $DATADIR/mustshe/raw/correct_ref/tmp/it_par.s \
    $DATADIR/mustshe/raw/correct_ref/tmp/es_speaker.csv \
    $DATADIR/mustshe/raw/correct_ref/tmp/es_category.csv \
    $DATADIR/mustshe/raw/correct_ref/tmp/es_gterms.csv \
    $DATADIR/mustshe/raw/correct_ref/tmp/fr_speaker.csv \
    $DATADIR/mustshe/raw/correct_ref/tmp/fr_category.csv \
    $DATADIR/mustshe/raw/correct_ref/tmp/fr_gterms.csv \
    $DATADIR/mustshe/raw/correct_ref/tmp/it_speaker.csv \
    $DATADIR/mustshe/raw/correct_ref/tmp/it_category.csv \
    $DATADIR/mustshe/raw/correct_ref/tmp/it_gterms.csv \
    $DATADIR/mustshe/raw/wrong_ref/tmp/es_par.s \
    $DATADIR/mustshe/raw/wrong_ref/tmp/fr_par.s \
    $DATADIR/mustshe/raw/wrong_ref/tmp/it_par.s \
    $DATADIR/mustshe/raw/wrong_ref/tmp/es_speaker.csv \
    $DATADIR/mustshe/raw/wrong_ref/tmp/es_category.csv \
    $DATADIR/mustshe/raw/wrong_ref/tmp/es_gterms.csv \
    $DATADIR/mustshe/raw/wrong_ref/tmp/fr_speaker.csv \
    $DATADIR/mustshe/raw/wrong_ref/tmp/fr_category.csv \
    $DATADIR/mustshe/raw/wrong_ref/tmp/fr_gterms.csv \
    $DATADIR/mustshe/raw/wrong_ref/tmp/it_speaker.csv \
    $DATADIR/mustshe/raw/wrong_ref/tmp/it_category.csv \
    $DATADIR/mustshe/raw/wrong_ref/tmp/it_gterms.csv \
    $DATADIR/mustshe/raw/correct_ref/ \
    $DATADIR/mustshe/raw/wrong_ref/  

rm -r $DATADIR/mustshe/raw/correct_ref/tmp/
rm -r $DATADIR/mustshe/raw/wrong_ref/tmp/
