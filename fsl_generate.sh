#!/bin/zsh
# $1 filename; $2 target_filename; $3 dim1; $4 dim2; $5 dim3
# ${@:6} brain area markers
# tpl: the data fitted to a template
# bet: brain extracted

postf=".nii.gz"
dirf=$(dirname $2)
basef=$(basename $2)

cp $1 $2

fslorient -deleteorient $2 # delete orientation
fslswapdim $2 $3 $4 $5 $2 # need check

# erase original information
fslorient -setqform 0.5 0 0 0 0 0.5 0 0 0 0 0.5 0 0 0 0 1 $2
fslorient -setsform 0.5 0 0 0 0 0.5 0 0 0 0 0.5 0 0 0 0 1 $2
fslorient -setqformcode 1 $2
fslorient -setsformcode 1 $2

# brain extraction
bet_file=$dirf/bet_$basef
tpl_bet_file=$dirf/tpl_bet_$basef
tpl_bet_mat=$dirf/tpl_bet_${basef%$postf}.mat
tpl_bet_inv_mat=$dirf/tpl_bet_${basef%$postf}_inv.mat

# # echo $bet_file $tpl_bet_file $tpl_bet_mat $tpl_bet_inv_mat
bet $2 $bet_file

# # register template to the monkey, it may take a while
flirt -in $bet_file -ref ../D99_v2.0_dist/D99_template.nii.gz -omat $tpl_bet_mat -out $tpl_bet_file
convert_xfm -omat $tpl_bet_inv_mat -inverse $tpl_bet_mat # inverse transformation


# transfer ebz back, 136 119 52 is the EBZ of D99
echo 136 119 52|img2imgcoord -src $tpl_bet_file -dest $bet_file  -xfm $tpl_bet_inv_mat >> $dirf/tpl_EBZ_${basef%$postf}.txt
for idx in ${@:6}
do
    mask_infile=$(find ./D99_mask -type f -name ${idx}_\*.nii.gz)
    basem=$(basename ${mask_infile})
    mask_outfile=$dirf/mask_${basem%$postf}_${basef}
    echo mask_outfile
    # transfer the template mask to original space mask
    flirt -in $mask_infile -ref $bet_file  -out $mask_outfile -applyxfm -init $tpl_bet_inv_mat
done
