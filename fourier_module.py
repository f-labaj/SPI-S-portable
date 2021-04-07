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
	M = int(1/scaling)
    
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
	
	if mode is "lowpass":
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
	
def reconstruct_image(resolution, scaling, fourier_coeff_list, mode):
    start = time.time()
	
    N = resolution
    M = int(1/scaling)
    
    fourier_spectrum = np.array(fourier_coeff_list)
    fourier_spectrum_2D = np.zeros((N,N))
    fourier_spectrum_2D_padded = np.zeros((N,N))
    reconstructed_image = np.zeros((N,N))
	
    if mode is "lowpass":
		# TODO - recheck correctness of np.reshape vs real fourier spectrum
        fourier_spectrum_2D = np.reshape(fourier_spectrum, (int(N/M), int(N/M)))
        fourier_spectrum_2D_padded = np.zeros((N,N),dtype=complex)
        fourier_spectrum_2D_padded[0:fourier_spectrum_2D.shape[0], 0:fourier_spectrum_2D.shape[1]] = fourier_spectrum_2D

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

    if mode is "lowpass":
        reconstructed_image = fft.ifft2(fourier_spectrum_2D_padded)
        
    else:
        reconstructed_image = fft.ifft2(fourier_spectrum_2D)

    end = time.time()
	
    print("\nReconstruction time: " + str(float(end-start)) + "s\n")
	
    return (reconstructed_image, fourier_spectrum_2D_padded)
	
# TODO -> pass original image etc.
def display_reconstructed_images(reconstructed_image, columns = 2, mode = "lowpass"):
	
	if mode is "lowpass":
		reconstructed_image_resized = resize(np.real(reconstructed_image), (N, N), anti_aliasing=1)
		show_images([image_gray, np.real(fourier_spectrum_2D), np.real(fourier_spectrum_2D_padded), np.real(reconstructed_image), np.real(reconstructed_image_padded), np.real(reconstructed_image_resized)], columns)

	elif mode is "midpass_alt":
		reconstructed_image_resized = resize(np.real(reconstructed_image), (N, N), anti_aliasing=1)
		show_images([image_gray, np.real(fourier_spectrum_2D), np.real(reconstructed_image)], columns)
		
	elif mode is "highpass":
		reconstructed_image_resized = resize(np.real(reconstructed_image), (N, N), anti_aliasing=1)
		show_images([image_gray, np.real(fourier_spectrum_2D), np.real(reconstructed_image), np.real(reconstructed_image_resized)], columns)
	
def analyze_reconstruction_PSNR(ground_truth, reconstructed_image):
	MSE = mean_squared_error(image_gray, np.real(reconstructed_image))
	PSNR = 10*math.log10(image_gray.max()**2 / MSE)

	print("\nMSE: " + str(MSE))
	print("PSNR: " + str(PSNR))
	
	# TODO!
	
def analyze_reconstruction_noise(ground_truth, reconstructed_image):
	noise = ground_truth - reconstructed_image
	# TODO!
	
	