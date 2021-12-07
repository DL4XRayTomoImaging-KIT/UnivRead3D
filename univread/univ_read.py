import os
import numpy as np
from glob import glob
from tqdm.auto import tqdm

import nrrd
import tifffile
import nibabel as nib

class TiffSequenceReader():
  def __init__(self, file_prefix, ext=''):
    if os.path.isdir(file_prefix):
      file_prefix = os.path.join(file_prefix, '*' + ext)
    self._filenames = sorted(glob(file_prefix))
    if not self._filenames:
      raise SequenceReaderError("No files matching `{}' found".format(file_prefix))
    self._lengths = {}
    self._file = None
    self._filename = None
    
  @property
  def num_images(self):
    num = 0
    for filename in self._filenames:
      num += self._get_num_images_in_file(filename)

    return num

  def read(self, index):
    if index < 0:
      # Enables negative indexing
      index += self.num_images
    file_index = 0
    while index >= 0:
      if file_index >= len(self._filenames):
        raise SequenceReaderError('image index greater than sequence length')
      index -= self._get_num_images_in_file(self._filenames[file_index])
      file_index += 1

    file_index -= 1
    index += self._lengths[self._filenames[file_index]]
    self._open(self._filenames[file_index])

    return self._file.pages[index].asarray()

  def _open(self, filename):
    self._file = tifffile.TiffFile(filename)
    self._filename = filename

  def _get_num_images_in_file(self, filename):
    if filename not in self._lengths:
      self._open(filename)
      self._lengths[filename] = len(self._file.pages)

    return self._lengths[filename]

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