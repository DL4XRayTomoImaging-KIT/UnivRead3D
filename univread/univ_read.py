import os
import numpy as np

import nrrd
import tifffile
import nibabel as nib

def read(file_):
  fname, ext = os.path.splitext(file_)
  
  if ext == '.tif' or ext == '.tiff':
    descriptor = tifffile.TiffFile(file_)
    img = descriptor.asarray()
    
    full_len = len(descriptor.pages)
    loaded_len = len(img)
 
    if loaded_len < full_len:
        img = np.concatenate([img, np.zeros((full_len - loaded_len, *img.shape[1:]), dtype=img.dtype)])
        for i in range(loaded_len, full_len):
            img[i] = descriptor.pages[i].asarray()
 
  elif ext == '.nrrd':
    img = nrrd.read(file_)[0]
  elif ext == '.nii':
    img = nib.load(file_)
    
  return img  