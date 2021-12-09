import os
import numpy as np
from glob import glob
from tqdm.auto import tqdm

import nrrd
import tifffile
import nibabel as nib


def read(file_):
  if os.path.isdir(file_):
    fprefix = os.path.join(file_, '*.tif*')
    fnames = sorted(glob(fprefix))
    
    file_0 = tifffile.TiffFile(fnames[0]).asarray()
    if len(file_0.shape) == 2:
      img = np.stack([tifffile.imread(fname) for fname in tqdm(fnames)])
    else:
      img = np.concatenate([tifffile.imread(fname) for fname in tqdm(fnames)], dtype=file_0.dtype)
  
  else:
    fname, ext = os.path.splitext(file_)
  
    if ext == '.tif' or ext == '.tiff':
      descriptor = tifffile.TiffFile(file_)
      img = descriptor.asarray()
      full_len = len(descriptor.pages)
      loaded_len = len(img)
 
      if loaded_len < full_len:
        img = np.concatenate(img, np.zeros((full_len - loaded_len, *img.shape[1:]), dtype=img.dtype))
        for i in range(loaded_len, full_len):
          img[i] = descriptor.pages[i].asarray()
 
    elif ext == '.nrrd':
      img = nrrd.read(file_)[0]
    elif ext == '.nii':
      img = nib.load(file_)
    
  return img