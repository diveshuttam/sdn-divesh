import numpy

from scipy.fftpack import fft,fft2, fftshift

import matplotlib.pyplot as plt

B=numpy.ones((4,4)); W=numpy.zeros((4,4))

signal = numpy.bmat("B,W;W,B")

onedimfft = fft(signal,n=16)

twodimfft = fft2(signal,shape=(16,16))

plt.figure()

plt.gray()

plt.subplot(121,aspect='equal')

plt.pcolormesh(onedimfft.real)

plt.colorbar(orientation='horizontal')

plt.subplot(122,aspect='equal')

plt.pcolormesh(fftshift(twodimfft.real))

plt.colorbar(orientation='horizontal')

plt.show()