# format test files into correct file format
mkdir -p $DATADIR/iwslt17_multiway/raw/test/prep

for sl in en it nl ro; do
    for tl in en it nl ro; do  
        if [ "$sl" != "$tl" ]; then
            # for f in $DATADIR/iwslt17_multiway/raw/test/orig/*\.${sl}; do
            for f in $DATADIR/iwslt17_multiway/raw/test/tst2017${sl}-${tl}.${sl}; do
                cp -f $f  $DATADIR/iwslt17_multiway/raw/test/prep/$sl-$tl.s
                cp -f $f  $DATADIR/iwslt17_multiway/raw/test/prep/$tl-$sl.t
            done
            # rm $f
        fi
    done
done