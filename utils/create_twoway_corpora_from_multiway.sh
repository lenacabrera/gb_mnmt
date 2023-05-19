path=$DATADIR/mustc/prepro_20000_subwordnmt/multiway

out_path_ES=$DATADIR/mustc/prepro_20000_subwordnmt/multiwayES
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayES
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayES/train
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayES/valid

out_path_FR=$DATADIR/mustc/prepro_20000_subwordnmt/multiwayFR
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayFR
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayFR/train
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayFR/valid

out_path_IT=$DATADIR/mustc/prepro_20000_subwordnmt/multiwayIT
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayIT
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayIT/train
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayIT/valid

out_path_es_it_fr=$DATADIR/mustc/prepro_20000_subwordnmt/multiwayESFRIT
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayESFRIT
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayESFRIT/train
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayESFRIT/valid

out_path_DE=$DATADIR/mustc/prepro_20000_subwordnmt/multiwayDE
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayDE
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayDE/train
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayDE/valid

out_path_EN=$DATADIR/mustc/prepro_20000_subwordnmt/multiwayEN
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayEN
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayEN/train
mkdir -p $DATADIR/mustc/prepro_20000_subwordnmt/multiwayEN/valid

 for set in train valid; do

     # es
     for f in $path/$set/es-*\.s; do
         cp -f $f $out_path_ES/$set
     done

     for f in $path/$set/*-es*\.s; do
         cp -f $f $out_path_ES/$set
     done

     for f in $path/$set/es-*\.t; do
         cp -f $f $out_path_ES/$set
     done

     for f in $path/$set/*-es*\.t; do
         cp -f $f $out_path_ES/$set
     done

     # fr
     for f in $path/$set/fr-*\.s; do
         cp -f $f $out_path_FR/$set
     done

     for f in $path/$set/*-fr*\.s; do
         cp -f $f $out_path_FR/$set
     done

     for f in $path/$set/fr-*\.t; do
         cp -f $f $out_path_FR/$set
     done

     for f in $path/$set/*-fr*\.t; do
         cp -f $f $out_path_FR/$set
     done

     # it
     for f in $path/$set/it-*\.s; do
         cp -f $f $out_path_IT/$set
     done

     for f in $path/$set/*-it*\.s; do
         cp -f $f $out_path_IT/$set
     done

     for f in $path/$set/it-*\.t; do
         cp -f $f $out_path_IT/$set
     done

     for f in $path/$set/*-it*\.t; do
         cp -f $f $out_path_IT/$set
     done

    # de
     for f in $path/$set/de-*\.s; do
         cp -f $f $out_path_DE/$set
     done

     for f in $path/$set/*-de*\.s; do
         cp -f $f $out_path_DE/$set
     done

     for f in $path/$set/de-*\.t; do
         cp -f $f $out_path_DE/$set
     done

     for f in $path/$set/*-de*\.t; do
         cp -f $f $out_path_DE/$set
     done
 done

partial_path=$DATADIR/mustc/prepro_20000_subwordnmt
for lan in multiwayES multiwayFR multiwayIT multiwayDE; do
    for set in train valid; do
        for f in $partial_path/$lan/$set/*; do
            # echo $lan $set
            # echo $f
            if [[ $lan != multiwayDE ]]; then
                echo $f
                cp -f $f $out_path_es_it_fr/$set
            fi
        done
    done
done
