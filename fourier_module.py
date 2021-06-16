# System modules
import sys
import time

# Numeric operations
import numpy as np
import math
import scipy.fft as fft
import imageio
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Image processing
from PIL import Image

import cv2 as cv

from skimage.morphology import square
from skimage import io
from skimage import color
from skimage import img_as_bool
from skimage.transform import resize
from skimage.filters import threshold_otsu, threshold_local
from skimage.filters.rank import threshold
from skimage.util import img_as_ubyte

from sklearn.metrics import mean_squared_error

import auxiliary_functions as aux

# TODO
def learned_thresholding():
	pass

# TODO
def dither_array(array):
	pass
	
# simple 3-mode thresholding function
def threshold_array(array, mode):
	# no threshold
	if mode == 0:	
		thresh_array = array
	
	# skimage local? threshold
	elif mode == 1:
		# possibly losing precision because of converting the array to uint8
		thresh_array = threshold(img_as_ubyte(array), square(3))
	
	# skimage local threshold
	elif mode == 2:
		thresh_array = threshold_local(array, 7)
		
	# global threshold
	# TODO: check if thresh_array + array works!
	elif mode == 3:
		thresh_array[array<thresh] = 0
		thresh_array[array>=thresh] = 1
		
	# Dithering
	elif mode == 4:
		thresh_array = dither_array(array)
		
	return thresh_array

# generate patterns for Fourier basis scan
# A and B are coefficients for pattern generation in cos function
def generate_patterns(resolution, scaling, A, B, threshold_flag, mode, patterns_directory):
	start = time.time()
	
	basis_list = []
	
	# phase shifts for the three-frame method
	phase_values = [0, 2*np.pi/3, 4*np.pi/3]
	
	# 4-image method, not currently supported
	#phase_values = [0, 0.5*np.pi, 1*np.pi, 1.5*np.pi]
	
	# currently only NxN
	N = resolution
	
	# compressive sensing parameter - how much of the signal will be used
	# changed from int to no type change! - 09.06.21
	M = 1/scaling
	
	# DEBUG
	print("Dimensions: " + str(resolution) + " x " + str(scaling))

	###
	
	# TODO - add selected pattern generation -> only generate discrete points of the Fourier plane, chosen by a function
	
	###
	
	# clear any previously generated patterns
	#aux.clear_directory(patterns_directory)
	
	###
	
	# TODO - generate patterns as inverse FFT - create Fourier plane and return to spatial domain!
	
	#if mode is "inverse":
		
	
	###
	
	# TODO - optimize nested for loops with numpy magical methods, LUT for cos calculation or similar
	
	###
	
	# DEBUG
	# test mode for checking and validating other patterns/sampling strategies
	if mode is "test":
		rng = int(N/M * 0.5)
		for f_x in range(-rng, rng, 1):
			for f_y in range(-rng, rng, 1):
				phase_mask_list = []
				for phase in phase_values:
					fourier_basis = np.zeros((N, N))
					for i in range(int(N)):
						for j in range(int(N)):
							fourier_basis[i, j] = A + B * np.cos(2*np.pi * f_x/N * i + 2*np.pi * f_y/N * j + phase)
					
					# TODO - add threshold method selection in menu
					##
					
					# TODO - add CNN/DL method of threshold
					##
					
					# TODO - add dithering
					##
					
					# basic thresholding
					fourier_basis = threshold_array(fourier_basis, threshold_flag)
					
					phase_mask_list.append(fourier_basis)
					
				# debug
				#show_images(phase_mask_list)
				basis_list.append(phase_mask_list)
				
				# debug
				print("F_x:" + str(f_x) + "\n" + "F_y:" + str(f_y) + "\n")
	
	# lowpass mode - CS is achieved by generating and using only low-valued frequencies
	elif mode is "lowpass":
		# indexing from 1 to prevent uniform fields for arguments 0
		for f_x in range(1, int(N/M)+1, 1):
			for f_y in range(1, int(N/M)+1, 1):
				phase_mask_list = []
				for phase in phase_values:
					fourier_basis = np.zeros((N, N))
					for i in range(int(N)):
						for j in range(int(N)):
							fourier_basis[i, j] = A + B * np.cos(2*np.pi * f_x/N * i + 2*np.pi * f_y/N * j + phase)
					
					# TODO - add threshold method selection in menu
					##
					
					# TODO - add CNN/DL method of threshold
					##
					
					# TODO - add dithering
					##
					
					# basic thresholding
					fourier_basis = threshold_array(fourier_basis, threshold_flag)
					
					phase_mask_list.append(fourier_basis)
					
				# debug
				#show_images(phase_mask_list)
				basis_list.append(phase_mask_list)
				
				# debug
				print("F_x:" + str(f_x) + "\n" + "F_y:" + str(f_y) + "\n")

	# other modes that use other parts of the Fourier space
	elif mode is "midpass_alt":
		for f_x in range(0, N, M):
			for f_y in range(0, N, M):
				phase_mask_list = []
				for phase in phase_values:
					fourier_basis = np.zeros((N, N))
					for i in range(int(N)):
						for j in range(int(N)):
							fourier_basis[i, j] = A + B * np.cos(2*np.pi * f_x/N * i + 2*np.pi * f_y/N * j + phase)
					
					# TODO - add threshold method selection in menu
					##
					
					# TODO - add CNN/DL method of threshold
					##
					
					
					
					# TODO - add dithering
					##
					
					# basic thresholding
					
					fourier_basis = threshold_array(fourier_basis, threshold_flag)
					
					phase_mask_list.append(fourier_basis)
				# debug
				#show_images(phase_mask_list)
				basis_list.append(phase_mask_list)
				# debug
				print("F_x:" + str(f_x) + "\n" + "F_y:" + str(f_y) + "\n")

	elif mode is "highpass":
		####################################################################
		# Temporary local parameters for highpass compressive sensing TODO!#
		####################################################################
		m_x = 4
		m_y = 4

		for f_x in range(m_x, int(N/M), 1):
			for f_y in range(m_y, int(N/M), 1):
				phase_mask_list = []
				for phase in phase_values:
					fourier_basis = np.zeros((N, N))
					for i in range(int(N)):
						for j in range(int(N)):
							fourier_basis[i, j] = A + B * np.cos(2*np.pi * f_x/N * i + 2*np.pi * f_y/N * j + phase)
					
					# TODO - add threshold method selection in menu
					##
					
					# TODO - add CNN/DL method of threshold
					##
					
					
					
					# TODO - add dithering
					##
					
					# basic thresholding
					
					fourier_basis = threshold_array(fourier_basis, threshold_flag)
					
					phase_mask_list.append(fourier_basis)
				# debug
				#show_images(phase_mask_list)
				basis_list.append(phase_mask_list)
				# debug
				print("F_x:" + str(f_x) + "\n" + "F_y:" + str(f_y) + "\n")
				
	end = time.time()

	print("\nFourier patterns generation time: " + str(float(end-start)) + " s\n")
	#print("\nSaving to pattern directory...")

	#aux.save_list_of_lists(basis_list, patterns_directory, 1)

	return basis_list

def mask_image(image, basis_list):
	start = time.time()
	
	masked_image_list = []
	
	for phase_mask_list in basis_list:
		masked_image_sub = []
		for phase_mask in phase_mask_list:
			masked_image_sub.append(image * phase_mask)
			
		masked_image_list.append(masked_image_sub)
		
	end = time.time()
	
	print("\nMasking time: " + str(float(end-start)) + "s\n")
	
	# flatten and plot the intensity vector list
	#aux.plot_list(np.array(masked_image_list).flatten)
	
	return masked_image_list

def calculate_fourier_coeffs(masked_image_list):
	start = time.time()

	fourier_coeff_list = []

	for masked_image_sub in masked_image_list:
		# calculate fourier coefficients (3-image method)
		fourier_coeff_list.append((2*masked_image_sub[0].sum() - masked_image_sub[1].sum() - masked_image_sub[2].sum()) + np.sqrt(3)*1j*(masked_image_sub[1].sum() - masked_image_sub[2].sum()))
			
	end = time.time()

	print("\nFourier coefficients calculation time: " + str(float(end-start)) + "s\n")

	return fourier_coeff_list
	
def reconstruct_image(resolution, scaling, fourier_coeff_list, mode, norm_mode, meas_file):
	start = time.time()
	
	N = resolution
	M = int(1/scaling)
	
	list_raw = fourier_coeff_list
	list_norm = []
	
	# normalize list of measurements
	# https://stackoverflow.com/questions/26785354/normalizing-a-list-of-numbers-in-python
	# for sum
	if norm_mode is 1:
		#list_norm = [float(i)/sum(list_raw) for i in list_raw]
		
		# debug
		list_norm = list_raw
	
	# for maximum
	elif norm_mode is 2:
		#list_norm = [float(i)/max(list_raw) for i in list_raw]
		
		# debug
		list_norm = list_raw
		
	# no normalization
	elif norm_mode is 0:
		list_norm = list_raw
	
	fourier_spectrum = np.array(list_norm)
	
	fourier_spectrum_2D = np.zeros((N,N))
	fourier_spectrum_2D_padded = np.zeros((N,N))
	reconstructed_image = np.zeros((N,N))
	
	if mode is "test":
		# reshape the measurement vector to 2D
		fourier_spectrum_2D = np.reshape(fourier_spectrum, (int(N/M), int(N/M)))
		
		#fourier_spectrum_2D_padded = np.zeros((N,N),dtype=complex)
		
		# since in the test mode the spectrum is centered, padding is applied to each side
		fourier_spectrum_2D_padded = np.pad(fourier_spectrum_2D, int((N - N/M)/2), mode='constant')
		
		#DEBUG
		aux.save_image_complex(np.real(fourier_spectrum_2D), "./GALLERY/fourier_unpadded", "")
		aux.save_image_complex(np.real(fourier_spectrum_2D_padded), "./GALLERY/fourier_padded", "")
	
	elif mode is "lowpass":
		# TODO - recheck correctness of np.reshape vs real fourier spectrum
		
		fourier_spectrum_2D = np.reshape(fourier_spectrum, (int(N/M), int(N/M)))
		
		fourier_spectrum_2D_padded = np.zeros((N,N),dtype=complex)
		fourier_spectrum_2D_padded[0:fourier_spectrum_2D.shape[0], 0:fourier_spectrum_2D.shape[1]] = fourier_spectrum_2D
		
		#DEBUG
		aux.save_image_complex(np.real(fourier_spectrum_2D), "./GALLERY/fourier_unpadded", "")
		aux.save_image_complex(np.real(fourier_spectrum_2D_padded), "./GALLERY/fourier_padded", "")
	
	# reconstruct from data saved to a file
	# TODO - change padding
	elif mode is "from_file":
		# load measurements from save directory
		fourier_coeff_list = aux.load_measurements(meas_file)
		
		# check if there is enough measurement points for reconstruction/the vector length has a root
		# if not - change the length to fit, cutting out or adding some data
		while aux.is_square(len(fourier_coeff_list)) is False:
			# remove last element of the list, loop will exit if it has a real root
			fourier_coeff_list.pop()
			
		fourier_spectrum_2D = np.reshape(fourier_spectrum, ((int(N/M)), (int(N/M))))
		
		
		# changed to equal padding on all sides, for test patterns
		fourier_spectrum_2D_padded = np.pad(fourier_spectrum_2D, int(N/2), mode='constant')
		#fourier_spectrum_2D_padded = np.zeros((N, N), dtype=complex)
		#fourier_spectrum_2D_padded[0:fourier_spectrum_2D.shape[0], 0:fourier_spectrum_2D.shape[1]] = fourier_spectrum_2D
		
		aux.save_image_complex(np.real(fourier_spectrum_2D), "./GALLERY/fourier_unpadded", "")
		aux.save_image_complex(np.real(fourier_spectrum_2D_padded), "./GALLERY/fourier_padded", "")
	
	# 'Real' mode based on measured intensity vector
	elif mode is "real":
		# check image sizes, prune unneeded/false measurements in main
		#N_pom = len(fourier_coeff_list)
		
		# check if there is enough measurement points for reconstruction/the vector length has a root
		# if not - change the length to fit, cutting out or adding some data
		while aux.is_square(len(fourier_coeff_list)) is False:
			# remove last element of the list, loop will exit if it has a real root
			fourier_coeff_list.pop()
		
		# ERROR!! Check below
		# returns ValueError for complex? list "ValueError: Non-string object detected for the array ordering. Please pass in 'C', 'F', 'A', or 'K' instead"
		fourier_spectrum_2D = np.reshape(fourier_spectrum, ((int(N/M)), (int(N/M))))
		
		#fourier_spectrum_2D_padded = np.zeros((N, N), dtype=complex)
		
		# changed to equal padding on all sides, for test patterns
		fourier_spectrum_2D_padded = np.pad(fourier_spectrum_2D, int((N - N/M)/2), mode='constant')
		#fourier_spectrum_2D_padded[0:fourier_spectrum_2D.shape[0], 0:fourier_spectrum_2D.shape[1]] = fourier_spectrum_2D
		
		aux.save_image_complex(np.real(fourier_spectrum_2D), "./GALLERY/fourier_unpadded", "")
		aux.save_image_complex(np.real(fourier_spectrum_2D_padded), "./GALLERY/fourier_padded", "")
		
	elif mode is "midpass_alt":
		fourier_spectrum_2D = np.reshape(fourier_spectrum, (int(N/M), int(N/M)))

	elif mode is "highpass":
		####################################################################
		# Temporary local parameters for highpass compressive sensing TODO!#
		####################################################################
		m_x = 4
		m_y = 4
	
		# DO ZMIANY -> uwzględnienie przerw 0-wych między zmierzonymi częstościami
		fourier_spectrum_zeros = np.dstack((fourier_spectrum,np.zeros_like(fourier_spectrum))).reshape(fourier_spectrum.shape[0],-1)
		fourier_spectrum_2D = np.reshape(fourier_spectrum_zeros, (int(N-m_x), int(N-m_y)))
		#fourier_spectrum_2D_padded = np.zeros((N,N),dtype=complex)
		#fourier_spectrum_2D_padded[m_x:fourier_spectrum_2D.shape[0], m_y:fourier_spectrum_2D.shape[1]] = fourier_spectrum_2D

	#if mode is "lowpass" or mode is "real":
	#	reconstructed_image = fft.ifft2(fourier_spectrum_2D_padded)
	#	
	#else:
	#	reconstructed_image = fft.ifft2(fourier_spectrum_2D)
	
	# reconstruct both the padded and unpadded spectrum using inverse FFT2D
	# added ifftshift as a solution to checkerboard-patterned positive and negative values in reconstructed image
	# thanks to https://stackoverflow.com/questions/10225765/checkerboard-pattern-after-fft
	reconstructed_image = fft.ifft2(fft.ifftshift(fourier_spectrum_2D_padded))
	reconstructed_image_unpadded = fft.ifft2(fft.ifftshift(fourier_spectrum_2D))
	
	end = time.time()
	print("\nReconstruction time: " + str(float(end-start)) + "s\n")
	
	# save reconstructions of the padded and unpadded spectrum:
	aux.save_image_complex(np.real(reconstructed_image_unpadded), "./GALLERY/image_unpadded_real", "")
	aux.save_image_complex(np.real(reconstructed_image), "./GALLERY/image_padded_real", "")
	
	# DEBUG
	# phase
	#aux.save_image_complex(np.angle(reconstructed_image_unpadded), "./GALLERY/image_unpadded_phase", "")
	#aux.save_image_complex(np.angle(reconstructed_image), "./GALLERY/image_padded_phase", "")
	
	# DEBUG
	# zero all negative values
	#aux.save_image_complex(np.real(reconstructed_image_unpadded.clip(min=0)), "./GALLERY/image_unpadded_clip", "")
	#aux.save_image_complex(np.real(reconstructed_image.clip(min=0)), "./GALLERY/image_padded_clip", "")

	return (reconstructed_image, reconstructed_image_unpadded, fourier_spectrum_2D, fourier_spectrum_2D_padded)