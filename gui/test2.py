from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

nyq = 22050
order = 10

lowcut2 = 300 / nyq
lowcut3 = 1000 / nyq
lowcut4 = 2500 / nyq
lowcut5 = 5000 / nyq
highcut1 = 299 / nyq
highcut2 = 999 / nyq
highcut3 = 2499 / nyq
highcut4 = 4999 / nyq

b1, a1 = signal.butter(5, highcut1, 'low')
w1, h1 = signal.freqz(b1, a1)

b2, a2 = signal.butter(4, [lowcut2, highcut2], 'bandpass')
w2, h2 = signal.freqz(b2, a2)

b3, a3 = signal.butter(7, [lowcut3, highcut3], 'bandpass')
w3, h3 = signal.freqz(b3, a3)

b4, a4 = signal.butter(8, [lowcut4, highcut4], 'bandpass')
w4, h4 = signal.freqz(b4, a4)

b5, a5 = signal.butter(10, lowcut5, 'highpass')
w5, h5 = signal.freqz(b5, a5)

w1 = w1 * nyq / (np.pi)
w2 = w2 * nyq / (np.pi)
w3 = w3 * nyq / (np.pi)
w4 = w4 * nyq / (np.pi)
w5 = w5 * nyq / (np.pi)
h1 = 20 * np.log10(abs(h1))
h2 = 20 * np.log10(abs(h2))
h3 = 20 * np.log10(abs(h3))
h4 = 20 * np.log10(abs(h4))
h5 = 20 * np.log10(abs(h5))



plt.semilogx(w1, h1, w2, h2, w3, h3, w4, h4, w5, h5)
axes = plt.gca()
axes.set_ylim([-40, 10])
plt.show()

