"""Binary data helpers for pdfsizeopt on Python 3.

pdfsizeopt was written for Python 2, where str is a byte string. To keep the
PDF parsing and serialization code (which relies heavily on str methods,
regexps and string literals) intact, pdfsizeopt represents binary data as
latin-1-decoded str objects: each character has an ordinal between 0 and 255,
corresponding to exactly one byte. This module contains the conversion
helpers needed at the boundaries (files, pipes, zlib, struct, hex).
"""

import binascii
import struct as _struct
import subprocess
import zlib as _zlib


def ToBytes(data):
  """Converts a latin-1 binary str to bytes."""
  if isinstance(data, (bytes, bytearray)):
    return bytes(data)
  return data.encode('latin-1')


def FromBytes(data):
  """Converts bytes to a latin-1 binary str."""
  if isinstance(data, str):
    return data
  return bytes(data).decode('latin-1')


def buffer(data, offset=0, size=None):
  """Replacement for the Python 2 buffer(...) builtin, returns a slice copy."""
  if size is None:
    return data[offset:]
  return data[offset : offset + size]


def HexEncode(data):
  """Like data.encode('hex') in Python 2."""
  return binascii.hexlify(ToBytes(data)).decode('ascii')


def HexDecode(data):
  """Like data.decode('hex') in Python 2, raises TypeError on bad input."""
  try:
    return binascii.unhexlify(ToBytes(data)).decode('latin-1')
  except (binascii.Error, ValueError) as e:
    raise TypeError(str(e))


def OpenLatin1(file_name, mode='rb'):
  """Opens a file for binary I/O using latin-1 str objects.

  Newline translation is disabled (newline=''), so data is read and written
  byte-by-byte.
  """
  return open(file_name, mode.replace('b', ''), encoding='latin-1',
              newline='')


class Latin1Popen(object):
  """Like os.popen(cmd, 'rb') or os.popen(cmd, 'wb') in Python 2.

  Reads and writes latin-1 str objects, and close() returns None on success
  or the exit status (shifted like os.system on Unix) on failure.
  """

  def __init__(self, cmd, mode='rb'):
    if 'r' in mode:
      self._proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
      self._file = self._proc.stdout
    elif 'w' in mode:
      self._proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
      self._file = self._proc.stdin
    else:
      raise ValueError('Bad popen mode: %r' % mode)

  def read(self, size=-1):
    return self._file.read(size).decode('latin-1')

  def readline(self):
    return self._file.readline().decode('latin-1')

  def write(self, data):
    self._file.write(ToBytes(data))

  def flush(self):
    self._file.flush()

  def close(self):
    self._file.close()
    status = self._proc.wait()
    if not status:
      return None
    if status < 0:  # Killed by a signal.
      return -status
    return status << 8

  def __iter__(self):
    return iter(self.readline, '')


class zlib_latin1(object):
  """Wrapper around the zlib module working on latin-1 str objects."""

  error = _zlib.error

  @staticmethod
  def compress(data, level=-1):
    return _zlib.compress(ToBytes(data), level).decode('latin-1')

  @staticmethod
  def decompress(data, *args):
    return _zlib.decompress(ToBytes(data), *args).decode('latin-1')

  @staticmethod
  def crc32(data, value=0):
    return _zlib.crc32(ToBytes(data), value)

  @staticmethod
  def adler32(data, value=1):
    return _zlib.adler32(ToBytes(data), value)

  class _Decompress(object):

    def __init__(self, *args):
      self._obj = _zlib.decompressobj(*args)

    def decompress(self, data):
      return self._obj.decompress(ToBytes(data)).decode('latin-1')

    def flush(self):
      return self._obj.flush().decode('latin-1')

    @property
    def unused_data(self):
      return self._obj.unused_data.decode('latin-1')

  @classmethod
  def decompressobj(cls, *args):
    return cls._Decompress(*args)


class struct_latin1(object):
  """Wrapper around the struct module working on latin-1 str objects."""

  error = _struct.error

  @staticmethod
  def pack(fmt, *args):
    return _struct.pack(fmt, *args).decode('latin-1')

  @staticmethod
  def unpack(fmt, data):
    result = _struct.unpack(fmt, ToBytes(data))
    if 's' in fmt:  # Convert back bytes values.
      result = tuple(FromBytes(v) if isinstance(v, bytes) else v
                     for v in result)
    return result

  @staticmethod
  def calcsize(fmt):
    return _struct.calcsize(fmt)
