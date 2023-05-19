PATH="$HOME/opt/bin:$HOME/perl5/bin${PATH:+:${PATH}}"; export PATH;
PERL5LIB="$HOME/perl5/lib/perl5${PERL5LIB:+:${PERL5LIB}}"; export PERL5LIB;
PERL_LOCAL_LIB_ROOT="$HOME/perl5${PERL_LOCAL_LIB_ROOT:+:${PERL_LOCAL_LIB_ROOT}}"; export PERL_LOCAL_LIB_ROOT;
PERL_MB_OPT="--install_base \"$HOME/perl5\""; export PERL_MB_OPT;
PERL_MM_OPT="INSTALL_BASE=$HOME/perl5"; export PERL_MM_OPT;

export HERE=~
export NMTDIR=$HERE/NMTGMinor #../../
export SCRIPTDIR=$NMTDIR/recipes/zero-shot #$NMTDIR/scripts
export WORKDIR=~/../../export/data2/lcabrera
export DATADIR=$WORKDIR/data
export OUTDIR=$WORKDIR/output

export OPTDIR=$HERE/opt
export MOSESDIR=$OPTDIR/mosesdecoder
export BPEDIR=$OPTDIR/subword-nmt
export FLORESDIR=$OPTDIR/flores

export PYTHON3=python3
export GPU=0

#cd -
