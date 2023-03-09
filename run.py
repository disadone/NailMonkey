
from utils import ProcessNiiFile


V_LPFC_byx=[330,335,339,355,374,392,405,422,425,431,441]
P_PFC_lyw=['9m','9d','46d','46v','11m','11l','10mr','10o',
           '12m','12r','12l','12o','14c','cd','NA','8Ad','8Bd','8Av','8Bs',
           '8Bm','45a','45b','13a','13m','13b','13l','F7','F6',
           '24b_prime','24a','24c_prime','24c','24b','24a_prime',
           'F2_(6DR_6DC)','F3','3a/b','F1_(4)','F5_(6Va_6Vb)','F4']
P_PFC_lyw_anno=[364,335,425,374,412,301,345,327,353,405,431,448,486,2,3,446,355,349,330,300,
 422,441,367,363,306,316,424,401,483,484,485,396,347,309,451,369,435,359,427,444]
assert(len(P_PFC_lyw)==len(P_PFC_lyw_anno))
if __name__=='__main__':
    # 306:13b OFC, 329: LIPv
    hdinfo = ProcessNiiFile('./data_example','anat.nii',
        dims=['x','y','z'],areas=[306,329])
 
