import os
import warnings
import numpy as np
from glob import glob
import dask.array as da

import nrrd
import tifffile
import nibabel as nib
from medpy.io import load as medload


def read(file_, lazy=False):
  
  if os.path.isdir(file_):  # paginated tiffs
    fprefix = os.path.join(file_, '*.tif*')
    fnames = sorted(glob(fprefix))
    
    if not lazy:
      file_0 = tifffile.imread(fnames[0])
      if len(file_0.shape) == 2:
        img = np.stack([tifffile.imread(fname) for fname in fnames])
      else:
        img = np.concatenate([tifffile.imread(fname) for fname in fnames])
    else:
      file_0 = tifffile.memmap(fnames[0])
      if len(file_0.shape) == 2:
        img = da.stack([tifffile.memmap(fname) for fname in fnames])
      else:
        img = da.concatenate([tifffile.memmap(fname) for fname in fnames])
  
  else:
    name = file_.split('.')
    fname, ext = name[0], name[1:]
    ext = f".{'.'.join(ext)}"  # ['nii', 'gz'] -> .nii.gz
  
    if ext in ['.tif', '.tiff']:
      descriptor = tifffile.TiffFile(file_)
      img = descriptor.asarray() if not lazy else tifffile.memmap(file_)
      full_len = len(descriptor.pages)
      loaded_len = len(img)
 
      # for multi-paginated tiffs
      if loaded_len < full_len:
        if lazy: raise Exception('Not implemented')
        img = np.concatenate([img, np.zeros((full_len - loaded_len, *img.shape[1:]))])
        for i in range(loaded_len, full_len):
          img[i] = descriptor.pages[i].asarray()
 
    elif ext == '.nrrd':
      if lazy: raise Exception('Not implemented')
      img = nrrd.read(file_)[0]
    elif ext in ['.nii', '.nii.gz']:
      img = nib.load(file_)
      if not lazy: img = np.array(img.dataobj)
    else:  # load with medpy as the default case
      if lazy: raise Exception('Not implemented')
      warnings.warn('unrecognized file extension, proceeding to load with medpy')
      img = medload(file_)[0]

  return img