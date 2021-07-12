import os, time
import glob

from numpy import save, load
import numpy as np
import matplotlib.pyplot as plt

from skimage import io
from skimage import color
from skimage import img_as_bool
from skimage.transform import resize

from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error

import scipy.misc

from PIL import Image

import paramiko

import math

import colorednoise as cn

# https://stackoverflow.com/questions/2489435/check-if-a-number-is-a-perfect-square
def is_square(integer):
	root = math.sqrt(integer)
	return integer == int(root + 0.5) ** 2

def connect_ssh(password):
	host = "192.168.7.2"
	port = 22
	username = "debian"
	# deprecated, password is passed from GUI input
	#password = input("Input password for debian@BBB: ")
	
	ssh = paramiko.SSHClient()
						
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	try:
		ssh.connect(host, port, username, password)					
	
	except:
		print("Connecting to BBB failed!")
		ssh = None
	
	return ssh
	
def execute_remote_command(ssh, command):
	stdin, stdout, stderr = ssh.exec_command(command)
	#stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
	
	return [stdin, stdout, stderr]
	
def close_ssh(ssh):
	ssh.close()

# TODO debug
# sometimes returns WinError 5 (Permission error) when trying to clear the dir
def clear_directory(directory):
	files_in_folder = glob.glob(directory + '/*')
	for f in files_in_folder:
		os.remove(f)
		
def save_list_of_lists(list_of_lists, directory, export_mode, resolution):
	print("PNG/BMP export mode: " + str(export_mode))

	# TODO - change to something more logical
	
	N = resolution
	
	# save as .npy for efficient binary IO
	if export_mode is False:
		i = 0
		for lst in list_of_lists:
			j = 0
			for el in lst:
				save(directory + 'name_' + str(i) + '_' + str(j) + '.npy', el, allow_pickle=False)
				j += 1
			i += 1
		
		print("Done saving patterns!")
		
	# save as .png in 1920x1080 for DMD display    
	elif export_mode is True:
		i = 0
		for lst in list_of_lists:
			j = 0
			for el in lst:
				# doesn't work well for small arrays
				#el_resized_square = np.resize(el, (360,360))
				
				# temporary workaround -> padding the small array
				arr_shape = np.shape(el)
				pad_dim_y = int((360 - arr_shape[0]) / 2)
				pad_dim_x = int((360 - arr_shape[1]) / 2)
				el_resized_square = np.pad(el, ((pad_dim_y, pad_dim_x), 
												(pad_dim_y, pad_dim_x)), 
												'constant', 
												constant_values=0)
				
				el_resized_padded = np.pad(el_resized_square, 
										   ((0,0), (140,140)), 
										   'constant', 
										   constant_values=0)
										   
				img = Image.fromarray((np.real(el_resized_padded) * 255 ))
				# change bit depth to 24-bit True Color - the only format accepted by DLP2000 default display software
				img_24 = img.convert("RGB")
				img_24.save(directory + str(i) + '_' + str(j) + '.bmp')
				j += 1
			i += 1
		
		print("Done saving patterns!")

	else:
		print("Export mode error!")

# https://stackoverflow.com/questions/6494102/how-to-save-and-load-an-array-of-complex-numbers-using-numpy-savetxt
def save_measurements(meas, file):
	# convert meas list to numpy array
	meas_arr = np.array(meas)
	# save the array as real (reinterpreted)
	np.savetxt(file + '.txt', meas_arr.view(float))

def save_measurement_vector(meas, file):
	# convert meas list to numpy array
	meas_arr = np.array(meas)
	# save the array as real (reinterpreted)
	np.savetxt(file + '.txt', meas_arr.view(int))

def load_measurements(file):
	# load the array as complex 
	try:
		meas_load = np.loadtxt(file + '.txt').view(complex)
		
	except:
		print("Error opening file!")
		meas_load = []
		
	return meas_load
	
def load_measurements_real(file):
	# load the array as complex 
	try:
		meas_load = np.loadtxt(file + '.txt').view(float)
		
	except:
		print("Error opening file!")
		meas_load = []
		
	return meas_load
	
# TODO mode
def load_list_of_lists(directory, mode):
	dir_list = os.listdir(directory)
	
	list_of_lists = []
	temp_list = []
	
	i = 0
	for el in dir_list:
		temp_list.append(load(directory + el))
		
		i+=1
		
		if i == 3:
			list_of_lists.append(temp_list)
			temp_list = []
			i = 0
			
	print("Done loading patterns!")

	return list_of_lists

def save_image(image, img_name, directory):
	#save(str(directory) + str(img_name) + '_.bmp', image, allow_pickle=False)
	img = Image.fromarray(image)
	img_24 = img.convert("RGB")
	img_24.save(str(directory) + str(img_name) + '.bmp')

def save_image_complex(image, img_name, directory):
	rescaled = (255.0 / image.max() * (image - image.min())).astype(np.uint8)
	#rescaled = image
	#rescaled *= 255.0 / rescaled.max()
	#rescaled = rescaled.astype(np.uint8)
	img = Image.fromarray(rescaled)
	img.save(str(directory) + str(img_name) + '.png')

def load_image(filename):
	image = io.imread(filename)
	
	image_gray = color.rgb2gray(image)

	return image_gray
	
def resize_image(image, resolution):
	N = resolution
	image_resized = resize(image, (N, N))
	
	return image_resized

# displays multiple images in one window
# doesn't work for reconstructions of real world measurements, due to a type error!
def show_images(images, cols = 2, titles = None):
	"""Display a list of images in a single figure with matplotlib.
	
	Parameters
	---------
	images: List of np.arrays compatible with plt.imshow.
	
	cols (Default = 1): Number of columns in figure (number of rows is 
						set to np.ceil(n_images/float(cols))).
	
	titles: List of titles corresponding to each image. Must have
			the same length as titles.
	"""
	plt.rcParams.update({'font.size': 16})
	
	assert((titles is None)or (len(images) == len(titles)))
	n_images = len(images)
	if titles is None: titles = ['Image (%d)' % i for i in range(1,n_images + 1)]
	fig = plt.figure()
	for n, (image, title) in enumerate(zip(images, titles)):
		a = fig.add_subplot(cols, np.ceil(n_images/float(cols)), n + 1)
		#if image.ndim == 2:
		plt.summer()
		plt.imshow(image)
		a.set_title(title)
	fig.set_size_inches(np.array(fig.get_size_inches()) * n_images)
	
	#plt.savefig('./GALLERY/reconstruction.eps', format='eps')
	plt.savefig('./GALLERY/reconstruction.png')
	#plt.show()
	
def plot_list(data_list):
	#x = list(range(1, len(data_list)+1))
	plt.xlabel("Pattern number")
	plt.ylabel("Measured intensity")
	plt.plot(data_list)
	
	#plt.savefig('./GALLERY/vector.eps', format='eps')
	plt.savefig('./GALLERY/vector.png')
	plt.show()
	
def calculate_PSNR(ground_truth, reconstructed_image):
	MSE = mean_squared_error(ground_truth, np.real(reconstructed_image))
	PSNR = 10*math.log10(ground_truth.max()**2 / MSE)

	return (MSE, PSNR)
	
def calculate_SSIM(ground_truth, reconstructed_image):
	SSIM = ssim(ground_truth, np.real(reconstructed_image))

	return SSIM

# TODO: change to 2D
# https://www.socsci.ru.nl/wilberth/python/noise.html
def spectrum_noise(spectrum_func, samples=1024, rate=44100):
    """ 
    make noise with a certain spectral density
    """
    freqs = np.fft.rfftfreq(samples, 1.0/rate)            # real-fft frequencies (not the negative ones)
    spectrum = np.zeros_like(freqs, dtype='complex')      # make complex numbers for spectrum
    spectrum[1:] = spectrum_func(freqs[1:])               # get spectrum amplitude for all frequencies except f=0
    phases = np.random.uniform(0, 2*np.pi, len(freqs)-1)  # random phases for all frequencies except f=0
    spectrum[1:] *= np.exp(1j*phases)                     # apply random phases
    noise = np.fft.irfft(spectrum)                        # return the reverse fourier transform
    noise = np.pad(noise, (0, samples - len(noise)), 'constant') # add zero for odd number of input samples
 
    return noise

# https://www.socsci.ru.nl/wilberth/python/noise.html
def pink_spectrum(f, f_min=0, f_max=np.inf, att=np.log10(2.0)*10):
    """
    Define a pink (1/f) spectrum
        f     = array of frequencies
        f_min = minimum frequency for band pass
        f_max = maximum frequency for band pass
        att   = attenuation per factor two in frequency in decibel.
                Default is such that a factor two in frequency increase gives a factor two in power attenuation.
    """
    # numbers in the equation below explained:
    #  0.5: take the square root of the power spectrum so that we get an amplitude (field) spectrum 
    # 10.0: convert attenuation from decibel to bel
    #  2.0: frequency factor for which the attenuation is given (octave)
    s = f**-( 0.5 * (att/10.0) / np.log10(2.0) )  # apply attenuation
    s[np.logical_or(f < f_min, f > f_max)] = 0    # apply band pass
    return s

# TODO
def add_noise(image, noise_type, magnitude):
	noisy_image = image
	N = image.shape[0]

	# https://numpy.org/doc/stable/reference/random/generated/numpy.random.rand.html
	if noise_type == "white":
		noisy_image += magnitude * np.random.rand(image.shape[0], image.shape[1])
		
	# https://www.socsci.ru.nl/wilberth/python/noise.html
	elif noise_type == "pink":
		pass

	elif noise_type == "pink_2":
		# check if it can take a tuple/N-dimensional
		cn.powerlaw_psd_gaussian(1, (N, N))
		
	elif noise_type == "blue":
		# a possible implementation: https://github.com/MomentsInGraphics/BlueNoise/blob/master/BlueNoise.py
		pass
		
	elif noise_type == "brown":
		# check if it can take a tuple/N-dimensional
		cn.powerlaw_psd_gaussian(2, (N, N))

	else:
		print("Incorrect noise type selected!")

	return noisy_image