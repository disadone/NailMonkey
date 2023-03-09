#!/bin/zsh
# $1 filename; $2 dim1; $3 dim2; $4 dim3; $5 bdim1; $6 bdim2; $7 bdim3;
# ${@:8} brain area markers
# rec: axes rectified
# bck: axes orignal
# tpl: data fitted to a template
# bet: brain extracted
# f: just name
# _file: with full path

postf=".nii.gz"


dirf=$(dirname $1)  # base directory, e.g. data/
basef=$(basename $1) # e.g. P.nii
mainf="${basef%.*}.nii.gz" # e.g. P
rec_file=$dirf/rec_$mainf
bet_file=$dirf/bet_$mainf
betf=$(basename $bet_file) # e.g. bet_P.nii.gz
recf=$(basename $rec_file) # e.g. rec_P.nii.gz
betrecf=bet$recf

# ______create rec file________
cp $1 $rec_file

fslorient -deleteorient $rec_file # delete orientation
fslswapdim $rec_file $2 $3 $4 $rec_file # need check

## erase original information
fslorient -setqform 0.5 0 0 0 0 0.5 0 0 0 0 0.5 0 0 0 0 1 $rec_file
fslorient -setsform 0.5 0 0 0 0 0.5 0 0 0 0 0.5 0 0 0 0 1 $rec_file
fslorient -setqformcode 1 $rec_file
fslorient -setsformcode 1 $rec_file




# ________brain extraction and fill into template__________

bet $1 $bet_file
betrec_file=$dirf/$betrecf
bet $rec_file $betrec_file
## bet rec file
tpl_betrec_file=$dirf/tpl_$betrecf
tpl_betrec_mat=$dirf/tpl_${betrecf%$postf}.mat
tpl_betrec_inv_mat=$dirf/tpl_${betrecf%$postf}_inv.mat
tpl_betrec_bet_mat=$dirf/tpl_betrec_${betf%$postf}.mat
## register template to the monkey, it may take a while
flirt -in $betrec_file -ref ./D99_v2.0_dist/D99_template.nii.gz -omat $tpl_betrec_bet_mat -out $tpl_betrec_file
convert_xfm -omat $tpl_betrec_inv_mat -inverse $tpl_betrec_bet_mat # inverse transformation

# ___EBZ related___
# transfer ebz back, 136 119 52 is the EBZ of D99
tpl_EBZ_rec_txt=$dirf/tpl_EBZ_${recf%$postf}.txt
echo 136 119 52|img2imgcoord -src $tpl_betrec_file -dest $betrec_file  -xfm $tpl_betrec_inv_mat | sed 1d > $tpl_EBZ_rec_txt

tpl_EBZ_txt=$dirf/tpl_EBZ_${mainf%$postf}.txt
IFS=$' ' set -A tpl_EBZ_rec $(cat $tpl_EBZ_rec_txt)
flirt -in $betrec_file -ref $bet_file -omat $tpl_betrec_bet_mat
echo ${tpl_EBZ_rec[@]}|img2imgcoord -src $betrec_file -dest $bet_file  -xfm $tpl_betrec_bet_mat | sed 1d > $tpl_EBZ_txt

# _____________mask generation and transfer to rec & bck____________
rec_mask_outfs_postfix=()
bck_mask_outfs_postfix=()
for idx in ${@:8}
do
    # ___mask in rec___
    mask_infile=$(find ./D99_mask -type f -name ${idx}_\*.nii.gz)
    maskm=$(basename ${mask_infile})
    rec_mask_outf=$dirf/mask_${maskm%$postf}_${recf}
    rec_mask_outfs_postfix+=$rec_mask_outf;rec_mask_outfs_postfix+="-max"
    # transfer the template mask to original space mask
    flirt -in $mask_infile -ref $betrec_file  -out $rec_mask_outf -applyxfm -init $tpl_betrec_inv_mat
    
    # ___mask in bck___
    bck_mask_outf=$dirf/mask_${maskm%$postf}_${mainf}
    bck_mask_outfs_postfix+=$bck_mask_outf;bck_mask_outfs_postfix+="-max"

    cp $rec_mask_outf $bck_mask_outf
    fslorient -deleteorient $bck_mask_outf
    fslswapdim $bck_mask_outf $5 $6 $7 $bck_mask_outf
    fslcpgeom $1 $bck_mask_outf 
done
# ____________ merge all mask files _________
merged_rec_mask_outf=$dirf/merged_mask_${recf}
fslmaths "${rec_mask_outfs_postfix[@]:0:-1}" $merged_rec_mask_outf

merged_bck_mask_outf=$dirf/merged_mask_${mainf}
fslmaths "${bck_mask_outfs_postfix[@]:0:-1}" $merged_bck_mask_outf