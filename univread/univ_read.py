import os
import warnings
import tempfile
import numpy as np
from glob import glob

import nrrd
import tifffile
import nibabel as nib
from medpy.io import load as medload


def read(file_, lazy=False):
  # file_: path of the img file to be read
  # lazy: setting to True will return memmap instead of np array
  
  # dir containing tiffs
  if os.path.isdir(file_):
    fnames = sorted(glob(f'{file_}/*.tif*'))
    
    if not lazy:
      file_0 = tifffile.imread(fnames[0])
      if len(file_0.shape) == 2:  # dir containing 2d tiffs
        img = np.stack([tifffile.imread(fname) for fname in fnames])
      else:  # dir containing 3d tiffs
        img = np.concatenate([tifffile.imread(fname) for fname in fnames])


    else:
      file_0 = tifffile.memmap(fnames[0])
      
      if len(file_0.shape) == 2:  # dir containing 2d tiffs
        shapes = [tifffile.memmap(fname).shape for fname in fnames]
        final_shape = (len(shapes), *shapes[0])
        
        with tempfile.NamedTemporaryFile() as f:
          img = np.memmap(f.name, dtype=file_0.dtype, mode='w+', shape=final_shape)

          for i,fname in enumerate(fnames):
            img[i] = tifffile.memmap(fname)
            img = np.memmap(f.name, dtype=file_0.dtype, mode='r+', shape=final_shape)
        
      else:  # dir containing 3d tiffs
        shapes = [tifffile.memmap(fname).shape for fname in fnames]
        sum_shapes = np.cumsum(shapes, axis=0)
        final_shape = (sum_shapes[-1][0], *shapes[0][1:])

        with tempfile.NamedTemporaryFile() as f:
          img = np.memmap(f.name, dtype=file_0.dtype, mode='w+', shape=final_shape)
          curr_indx = 0

          for i,fname in enumerate(fnames):
            nxt_indx = sum_shapes[i][0]
            img[curr_indx:nxt_indx] = tifffile.memmap(fname)
            curr_indx = nxt_indx
            img = np.memmap(f.name, dtype=file_0.dtype, mode='r+', shape=final_shape)



  # single files
  else:
    name = file_.split('.')
    fname, ext = name[0], name[1:]
    ext = f".{'.'.join(ext)}"  # ['nii', 'gz'] -> .nii.gz

    if ext in ['.tif', '.tiff']:
      descriptor = tifffile.TiffFile(file_)
      img = tifffile.memmap(file_)
      full_len = len(descriptor.pages)
      loaded_len = len(img)
  
      # for handling multi-page tiffs
      if loaded_len < full_len:
        if not lazy:
          img = np.array([page.asarray() for page in descriptor.pages])
  
        else:
          final_shape = (full_len, *img.shape[1:])
          with tempfile.NamedTemporaryFile() as f:
            img = np.memmap(f.name, dtype=img.dtype, mode='w+', shape=final_shape)
            for i, page in enumerate(descriptor.pages):
              img[i] = page.asarray()
              img = np.memmap(f.name, dtype=img.dtype, mode='r+', shape=final_shape)
 
    elif ext == '.nrrd':
      if lazy: raise NotImplementedError(f'lazy reading not implemented for {ext}')
      img = nrrd.read(file_)[0]
    elif ext in ['.nii', '.nii.gz']:
      img = nib.load(file_)
      if not lazy: img = np.array(img.dataobj)
    else:  # load with medpy as the default case
      if lazy: raise NotImplementedError(f'lazy reading not implemented for {ext}')
      warnings.warn('unrecognized file extension, proceeding to load with medpy')
      img = medload(file_)[0]

  return img