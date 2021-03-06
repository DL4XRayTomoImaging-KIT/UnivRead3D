import os
import warnings
import tempfile
import numpy as np
from glob import glob

import nrrd
import tifffile
import nibabel as nib
from medpy.io import load as medload



def read_tiffdir(fpath, lazy):
  fnames = sorted(glob(f'{fpath}/*.tif*'))
  file_0 = tifffile.memmap(fnames[0]) if lazy else tifffile.imread(fnames[0])

  if not lazy:
    if len(file_0.shape) == 2:  # dir containing 2d tiffs
      img = np.stack([tifffile.imread(fname) for fname in fnames])
    else:  # dir containing 3d tiffs
      img = np.concatenate([tifffile.imread(fname) for fname in fnames])

  else:
    shapes = np.array([tifffile.memmap(fname).shape for fname in fnames])

    if len(file_0.shape) == 2:  # dir containing 2d tiffs
      final_shape = (len(shapes), *shapes[0])

      with tempfile.NamedTemporaryFile() as f:
        img = np.memmap(f.name, dtype=file_0.dtype, mode='w+', shape=final_shape)
        for i,fname in enumerate(fnames):
          img[i] = tifffile.memmap(fname)
          img = np.memmap(f.name, dtype=file_0.dtype, mode='r+', shape=final_shape)

    else:  # dir containing 3d tiffs
      final_shape = (sum(shapes[:,0]), *shapes[0][1:])

      with tempfile.NamedTemporaryFile() as f:
        img = np.memmap(f.name, dtype=file_0.dtype, mode='w+', shape=final_shape)
        indx = 0
        for fname in fnames:
          descriptor = tifffile.TiffFile(fname)
          for page in descriptor.pages:
            img[indx] = page.asarray()
            img = np.memmap(f.name, dtype=file_0.dtype, mode='r+', shape=final_shape)
            indx += 1

  return img


def read_tifffile(file_, lazy):
  descriptor = tifffile.TiffFile(file_)
  img = tifffile.memmap(file_) if lazy else tifffile.imread(file_)
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

  return img


def read_nii(file_, lazy):
  img = nib.load(file_)
  img_dtype = img.header.get_data_dtype()
  img = img.dataobj

  if not lazy:
    img = np.array(img)
  else:  
    img = np.asanyarray(img)
    if type(img) != np.memmap:
      raise TypeError(f'expected memmap but got {type(img)}')
    if img_dtype != img.dtype:
      raise TypeError(f"dtype in header ({img_dtype}) doesn't match the memmap dtype ({img.dtype})")  

  return img


def read_nrrd(file_, lazy):
  if lazy:
    raise NotImplementedError('lazy reading not implemented for .nrrd')
  img = nrrd.read(file_)[0]
  return img


def read_default(file_, lazy):
  if lazy:
    raise NotImplementedError('lazy reading not implemented for this extension')
  warnings.warn('unrecognized file extension, proceeding to load with medpy')
  img = medload(file_)[0]
  return img


def read_np(file_, lazy):
  """
    Reads and returns file with standard numpy methods.
  """
  mmap_mode = 'r' if lazy else None
  img = np.load(file_, mmap_mode=mmap_mode)
  return img



def read(file_, lazy=False):
  # file_: path of the img file to be read
  # lazy: setting to True will return memmap instead of np array

  # dir containing tiffs
  if os.path.isdir(file_):
    reader = read_tiffdir

  # single files
  else:
    if file_.endswith(('.tif', '.tiff')):
      reader = read_tifffile
    elif file_.endswith('.nrrd'):
      reader = read_nrrd
    elif file_.endswith(('.nii', '.nii.gz')):
      reader = read_nii
    elif file_.endswith('.npy'):
      reader = read_np
    else:  # load with medpy as the default case
      reader = read_default
  
  img = reader(file_, lazy)
  return img
