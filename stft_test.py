import numpy as np
from scipy import signal
rng1 = np.random.default_rng(12345)
rng2 = np.random.default_rng(4567)
fftn = 768

noise1 = rng2.normal(scale=np.sqrt(1),size=768*3)+rng1.normal(scale=np.sqrt(1),size=768*3)*1j
noise2 = rng1.normal(scale=np.sqrt(1),size=768*3)+rng2.normal(scale=np.sqrt(1),size=768*3)*1j

_, _, outsig1 = signal.stft(np.append(np.zeros(fftn//2),noise1), window='hann', nperseg=fftn, noverlap=fftn // 2, boundary=None, padded=False, return_onesided=False)
_, _, outsig2 = signal.stft(np.append(noise1[len(noise1)-fftn//2:],noise2), window='hann', nperseg=fftn, noverlap=fftn // 2, boundary=None, padded=False, return_onesided=False)

_, rxsig1 = signal.istft(np.append(np.zeros((fftn,1)),outsig1,axis=1), window='hann', nperseg=fftn, noverlap=fftn//2, boundary=None, input_onesided=False)
_, rxsig2 = signal.istft(np.append(outsig1[:,-2:-1],outsig2, axis=1), window='hann', nperseg=fftn, noverlap=fftn//2, boundary=None, input_onesided=False)

rxsigtotal = np.append(rxsig1[fftn:],rxsig2[fftn:])
noisetotal = np.append(noise1,noise2)

print("testing")
print(np.testing.assert_almost_equal(rxsigtotal, noisetotal, decimal=10))
print("rx")
print(rxsigtotal)
print("tx")
print(noisetotal)


_, rxsig1 = signal.istft(np.append(np.zeros((fftn,1)),outsig1[:,:4],axis=1), window='hann', nperseg=fftn, noverlap=fftn//2, boundary=None, input_onesided=False)
print(rxsig1.shape)
_, rxsig2 = signal.istft(np.append(outsig1[:,3:],outsig2[:,:2], axis=1), window='hann', nperseg=fftn, noverlap=fftn//2, boundary=None, input_onesided=False)
print(rxsig2.shape)
_, rxsig3 = signal.istft(outsig2[:,1:], window='hann', nperseg=fftn, noverlap=fftn//2, boundary=None, input_onesided=False)
print(rxsig3.shape)

rxsigtotal = np.concatenate((rxsig1[fftn:],rxsig2[fftn:],rxsig3[fftn:]))

print("testing")
print(np.testing.assert_almost_equal(rxsigtotal, noisetotal, decimal=10))
