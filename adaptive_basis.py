import numpy as np

import scipy.fft as fft
from scipy.interpolate import interp2d
from sklearn import preprocessing

from matplotlib import pyplot as plt

import fourier_module as fourier
import auxiliary_functions as aux

import imageio

import sys

# Interpolates a given image to a given resolution, using linear, cubic or quintic approximation
# alternative method: https://github.com/idealo/image-super-resolution
def interpolate_image(image, new_resolution, interp_type='linear'):
	image_placeholder = np.ones((new_resolution, new_resolution))
	x = np.linspace(0, image_placeholder.shape[1], image.shape[1])
	y = np.linspace(0, image_placeholder.shape[0], image.shape[0])
	
	interpolation_function = interp2d(x, y, np.real(image), kind=interp_type)

	x_new = np.arange(0, image_placeholder.shape[1])
	y_new = np.arange(0, image_placeholder.shape[0])

	interpolated_image = interpolation_function(x_new, y_new)
	
	return interpolated_image
	
# performs adaptive scanning of an image and returns adaptive patterns
def scan(image, resolution, cs_ratio):
	N = resolution
	M = cs_ratio
	
	adaptive_patterns = []
	
	images1 = []
	images2 = []
	
	MSE_vals = []
	PSNR_vals = []
	SSIM_vals = []
	CS_vals = []
	
	p = 0.05
	
	# iteration number, currently hard-coded
	for i in range(1, 11, 1):
		print("\nAdaptive iteration no. " + str(i))
		
		# set an initial compression ratio for the coarse scan, currently hard-coded
		M_coarse = M*0.1
		
		# for the first iteration, generate and reconstruct the image from coarse patterns
		if i == 1:
			# generate low-pass patterns
			patterns = fourier.generate_patterns(N, M_coarse, 0.5, 0.5, 0, 'test', "./PATTERNS/")
			reconstructed_image, _, _, reconstructed_spectrum = fourier.reconstruct_image(	N,
																							M_coarse, 
																							fourier.calculate_fourier_coeffs(fourier.mask_image(image, patterns)), 
																															 'test', 
																															 0, 
																															 0)
			
		# for the other iterations, reconstruction using previously generated adaptive patterns
		else:
			reconstructed_image, _, _, reconstructed_spectrum = fourier.reconstruct_image(	N, 
																							M, 
																							fourier.calculate_fourier_coeffs(fourier.mask_image(image, adaptive_patterns)), 
																																'test', 
																																0, 
																																0)
			
		# interpolation of the image, to 2Nx2N
		interpolated_image = interpolate_image(reconstructed_image, N*2, 'linear')
		
		# FFT of the interpolated image
		interpolated_spectrum = fft.fftshift(fft.fft2(interpolated_image))
			
		# sort the spectrum by modulus
		sorted_array = np.flip(np.sort(np.abs(interpolated_spectrum), axis=None))

		# set the threshold by choosing a value, defined by the percentage p
		threshold = np.abs(sorted_array[int(p * sorted_array.shape[0])])
		print("Current threshold value: " + str(threshold))
		
		# alternative method, using a constant, hard-coded value
		#highest_value_indices = np.abs(interpolated_spectrum) > np.amax(np.abs(interpolated_spectrum)) / (1500/i)
		
		# get a 2Nx2N mask of the chosen/thresholded patterns
		highest_value_indices = np.abs(interpolated_spectrum) > threshold
			
		# reduce size to the original NxN
		highest_value_indices_orig = highest_value_indices[int(0.5*N):int(1.5*N), int(0.5*N):int(1.5*N)]
			
		# generate patterns based on the adaptive mask
		adaptive_patterns = fourier.generate_patterns_adaptive(N, 1, highest_value_indices_orig.astype(int))

		###

		# calculate quality metrics of the reconstructed image
		MSE, PSNR = aux.calculate_PSNR(image, reconstructed_image)
		SSIM = aux.calculate_SSIM(image, reconstructed_image)
			
		print("MSE: " + str(MSE))
		print("PSNR: " + str(PSNR))
		print("SSIM: " + str(SSIM))
		
		CS = np.count_nonzero(highest_value_indices_orig) / N**2
		
		print("\nCurrent compression ratio: " + str(CS))

		# generate a gif of the adaptive scan
		images1.append(np.real(reconstructed_image))
		images2.append(highest_value_indices_orig.astype(int))

		MSE_vals.append(MSE)
		PSNR_vals.append(PSNR)
		SSIM_vals.append(SSIM)
		CS_vals.append(CS)

	# generate gifs from the iterations
	imageio.mimsave('adaptive_reconstruction.gif', images1)
	imageio.mimsave('adaptive_mask.gif', images2)
		
	plt.plot(MSE_vals)
	plt.xlabel("Iteracja")
	plt.ylabel("MSE")
	plt.savefig('MSE.png', bbox_inches='tight')
	
	plt.close()
	
	plt.plot(PSNR_vals)
	plt.xlabel("Iteracja")
	plt.ylabel("PSNR")
	plt.savefig('PSNR.png', bbox_inches='tight')
	
	plt.close()
	
	plt.plot(SSIM_vals)
	plt.xlabel("Iteracja")
	plt.ylabel("SSIM")
	plt.savefig('SSIM.png', bbox_inches='tight')
	
	plt.close()
	
	plt.plot(CS_vals)
	plt.xlabel("Iteracja")
	plt.ylabel("CS_ratio")
	plt.savefig('CS_ratio.png', bbox_inches='tight')
		
	plt.close()
		
	# return the generated adaptive patterns
	return (adaptive_patterns, interpolated_image, reconstructed_image, highest_value_indices_orig.astype(int))
	