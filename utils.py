
import numpy as np
import re,subprocess
import os
import matplotlib.pyplot as plt
import nibabel as nib
aa=np.asarray

def load_nii(file_path):
    """wrap load nii file using nibabel

    Parameters
    ----------
    file_path : str
        nii file path

    Returns
    -------
    nibabel.nifti1.Nifti1Image, ndarray[float,3]
        mri data
    """    
    epi_img=nib.load(file_path)
    return epi_img,epi_img.get_fdata()
def save_nii(file_path,img_data,epi_img):
    """warp save nii file using nibabel

    Parameters
    ----------
    file_path : str
        nii file path
    img_data : ndarray[float,3]
        image data
    epi_img : nibabel.nifti1.Nifti1Image
        Nifti1Image object for affine and header while saving
    """    
    nii=nib.Nifti1Image(img_data, epi_img.affine, epi_img.header)
    nib.save(nii,file_path)


def show_slices(epi_img_data,EBZ=None,title=None,fig=None,axes=None):
    """show slices of MRI data

    Parameters
    ----------
    epi_img_data : ndarray[float,3]
        image data, ranging from 0 to 1000
    EBZ : ndarray[float](3), optional
        ear bar zero, if none, EBZ is not shown, by default None
    fig : matplotlib.Figure
        fig for slice
    axes : ndarray[matplotlib.Axes](3)
        axes for slice
    """    

    if fig is None or axes is None:
        fig, axes = plt.subplots(1,3,figsize=(10,3),dpi=300)

    if EBZ:
        sg0,cr0,hz0=EBZ
    else:
        sg0,cr0,hz0=np.round(aa(epi_img_data.shape)//2).astype(int)
    sagittal = epi_img_data[sg0, :, :].T
    coronal = epi_img_data[:, cr0, :].T
    horizontal = epi_img_data[:, :, hz0].T

    sagittal[sagittal==-1]=sagittal.max()
    coronal[coronal==-1]=coronal.max()
    horizontal[horizontal==-1]=horizontal.max()


    
    axes[0].imshow(sagittal, cmap="gray", origin="lower")
    axes[1].imshow(coronal, cmap="gray", origin="lower")
    axes[2].imshow(horizontal, cmap="gray", origin="lower")
    
    axes[0].set(title='sagittal')
    axes[1].set(title='coronal')
    axes[2].set(title='horizontal')
    if EBZ:
        axes[0].plot(cr0,hz0,'ro',markersize=3)
        axes[1].plot(sg0,hz0,'ro',markersize=3)
        axes[2].plot(sg0,cr0,'ro',markersize=3)

    if title:
        fig.suptitle(title,y=1.05)

def ArrangeHeader(hdinfo):
    """turn header string to python dict

    Parameters
    ----------
    hdinfo : str
        header information extracted using `fslhd` command

    Returns
    -------
    dict
        header file with dict
    """
    return dict([re.split("\t\t|\t",s) for s in hdinfo.split('\n') if '\t' in s])

def DetermineOrientTransformation(hdinfo):
    """determine the direction the rotate the MRI data to correct head direction

    Parameters
    ----------
    hdinfo : dict
        header information extracted using `fslhd` command and transferred into Python dict

    Returns
    -------
    list[str](3)
        the correct axes for `fslswapdim` command 
    """    
    assert(
        hdinfo['sform_xorient']==hdinfo['qform_xorient'] and
        hdinfo['sform_yorient']==hdinfo['qform_yorient'] and
        hdinfo['sform_zorient']==hdinfo['qform_zorient'])
    # the correct orientation
    oris2loc={'Right-to-Left':0, 'Inferior-to-Superior':1, 'Posterior-to-Anterior':2}
    axes=[None]*3
    for i,s in enumerate(['x','y','z']):
        ori=hdinfo[f'sform_{s}orient']
        print(s,ori)
        if not ori in oris2loc: 
            sign='-' # switch the direction
            new_ori='-to-'.join(ori.split('-to-')[::-1])
        else:
            sign=''
            new_ori=ori
        axes[oris2loc[new_ori]]=sign+s
    return axes

# def MarkLIP(epi_img_data,EBZ,pixdim=0.5):
#     """mark LIP area accroding to Saleem,Nikos Atlas
#     Sagittal
#     - P291 LIP LIPv +6mm from midline
#     - P293~P317 LIPd LIPv +7~+19mm from midline
#     - P319 LIPd +20mm from midline

#     Rostral
#     - P211 LIP +8mm rostral to EBZ
#     - P217 LIPd/LIPv +7~+5mm rostral to EBZ
#     - P219~P237 LIPd LIPv +4~-5mm rostral to EBZ (separated)
#     - P239 LIP -6mm rostral to EBZ

#     Horizontal
#     - P97~P115 +28~+37mm dorsal to EBZ

#     Parameters
#     ----------
#     epi_img_data : ndarray[float,3]
#         image data, ranging from 0 to 1000
#     EBZ : ndarray[float](3)
#         ear bar zero
#     pixdim : float, optional
#         pixel distance , by default 0.5
#         same pixel distance for different dimension is assumed
#     Returns
#     -------
#     ndarray[float,3]
#         image data with the correspondant area marked with 1000
#     """    
#     ebz_sg_range=(aa([6,20+1])/pixdim).astype(int)
#     ebz_cr_range=(aa([-6,8+1])/pixdim).astype(int)
#     ebz_hz_range=(aa([28,37+1])/pixdim).astype(int)
#     area_epi_img_data=epi_img_data.copy()
#     sg_l,sg_r=EBZ[0]+ebz_sg_range
#     cr_l,rs_r=EBZ[1]+ebz_cr_range
#     hz_l,hz_r=EBZ[2]+ebz_hz_range
#     area_epi_img_data[sg_l:sg_r,cr_l:rs_r,hz_l:hz_r]=-1 # as the area marker
#     return area_epi_img_data

def ProcessNiiFile(main_folder,nii_file,dims=None,areas=None):
    """The pipeline to process nii file

    Parameters
    ----------
    main_folder : str
        the main folder name
    nii_file : str
        the structural nii file
    dims : list[str](3)
        rotate the nii file direction for `fsloreint` command , by default None
    areas : list[int]
        list of No. in brain area excel file
    
    Returns
    -------
    tuple(str)
        direction rectified nii file and the original nii file header info
    """
    if areas:
        str_areas=' '.join([str(int(a)) for a in areas])
    name = nii_file.split('.')[0]
    nii_file = f"{main_folder}{nii_file}"
    new_nii_file = f"{main_folder}rec_{name}.nii.gz" # rectified file
    print(nii_file)
    print(os.getcwd())
    hdinfo_str = subprocess.Popen(f"fslhd {nii_file}", 
        stdout=subprocess.PIPE, shell=True).communicate()[0].decode('ascii')
    hdinfo = ArrangeHeader(hdinfo_str)
    if dims is None:
        dim1,dim2,dim3 = DetermineOrientTransformation(hdinfo)
    else:
        dim1,dim2,dim3=dims
    
    print("dimension direction",dim1,dim2,dim3)
    if areas:
        process_info = subprocess.Popen(f"zsh fsl_generate.sh {nii_file} {new_nii_file} {dim1} {dim2} {dim3} {str_areas}",stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    else:
        process_info = subprocess.Popen(f"zsh fsl_generate.sh {nii_file} {new_nii_file} {dim1} {dim2} {dim3}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    print(process_info.communicate())
    return new_nii_file,hdinfo