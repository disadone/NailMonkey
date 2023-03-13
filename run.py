
from utils import ProcessNiiFile

# if __name__=='__main__':
#     # 306:13b OFC, 329: LIPv
#     hdinfo = ProcessNiiFile('./data_example','anat.nii',
#         dims=['x','y','z'],areas=[306,329])
 
if __name__=='__main__':
    # 306:13b OFC, 329: LIPv
    hdinfo = ProcessNiiFile('./private/data_private/data_Flamenco_20221020','Flamenco_20221020.nii.gz',areas='all')