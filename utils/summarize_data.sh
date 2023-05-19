# path=$1
# path=$DATADIR/mustshe/prepro_20000_subwordnmt/correct_ref
path=$DATADIR/mustc/raw/twoway/train
out=/home/lperez/output/data_summary/summary_mustc_twoway_train.csv

rm -f $out

for f in $path/*; do
    filename="$(basename "$f")"
    linecount=$(wc -l < $f)
    echo "$filename;$linecount" >> $out
done
