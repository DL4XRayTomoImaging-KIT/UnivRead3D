import os
import numpy as np

import nrrd
import tifffile
import nibabel as nib

def read(file_):
  fname, ext = os.path.splitext(file_)
  
  if ext == '.tif' or ext == '.tiff':
    img = tifffile.imread(file_)
    img = np.swapaxes(img, 0, -1)
  elif ext == '.nrrd':
    img = nrrd.read(file_)[0]
  elif ext == '.nii':
    img = nib.load(file_)
    
  return img  