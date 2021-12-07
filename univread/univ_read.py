import os
import numpy as np
from tqdm.auto import tqdm

import nrrd
import tifffile
import nibabel as nib

from concert.readers import TiffSequenceReader

def read(file_):
  if os.path.isdir(file_):
    seq_reader = TiffSequenceReader(os.path.join(file_, '*.tif*'))
    pg_0 = seq_reader.read(0)

    img = np.zeros((seq_reader.num_images, *pg_0.shape), dtype=pg_0.dtype)
    for i in tqdm(range(seq_reader.num_images)):
      img[i] = seq_reader.read(i)
  
  else:
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