import numpy as np

x = np.array([1,2,3,4,5]*2)
frate = 2
data = x - np.average(x)
w = np.fft.fft(data)
print("w",w)
freqs = np.fft.fftfreq(len(w))
print("freqs",freqs)
print(freqs.min(), freqs.max())
# (-0.5, 0.499975)
# Find the peak in the coefficients
print("np.abs(w)", np.abs(w))
idx = np.argmax(np.abs(w))
print("idx", idx)
freq = freqs[idx]
print("freq",freq)
freq_in_hertz = abs(freq * frate)
print("freq_in_hertz", freq_in_hertz)
print("nyquist freq_in_hertz", 2*freq_in_hertz)

print("time period", 1/freq_in_hertz)
print("nyquist time period", 1/(2*freq_in_hertz))
