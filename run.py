
from utils import ProcessNiiFile





if __name__=='__main__':
    # 306:13b OFC, 329: LIPv
    nii_file_path,hdinfo = ProcessNiiFile('./data_example/','anat.nii',
        dims=['x','y','z'],areas=[306,329])
 