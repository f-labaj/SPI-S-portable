import sys
import time

import numpy as np
import math
import scipy.fft as fft
import imageio
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from PIL import Image

import cv2 as cv

from skimage import io
from skimage import color
from skimage import img_as_bool
from skimage.transform import resize
#from skimage.filters import threshold_otsu, threshold_adaptive

from scipy.linalg import hadamard

from sklearn.metrics import mean_squared_error

# odpalenie silnika matlaba pod eng, do IFWHT
#import matlab.engine
#eng = matlab.engine.start_matlab()

# N<512 - rozmiar Leny
#N = 64

# wspolczynnik przeskalowania
#M = 0.1

# wczytanie obrazu
# image = io.imread("airplane.png")
# image_gray = color.rgb2gray(image)

# image_gray = resize(image_gray, (N, N))

# start1 = time.time()

# hadamard_matrix = hadamard(N**2)

# mask_list = []


# TODO
# WIP!
def generate_patterns(resolution):
    N = resolution

    for i in range(int(N**2)):
        mask_full = np.resize(hadamard_matrix[i,:], (N, N))
        
        mask_pos = mask_full.copy()
        mask_neg = mask_full.copy()
        
        mask_pos[mask_pos<0] = 0
        mask_pos[mask_pos>0] = 1
        mask_neg[mask_neg>0] = 0
        mask_neg[mask_neg<0] = 1

        mask_list.append([mask_pos, mask_neg])
        
    return mask_list

def mask_image():
    masked_image_list = []
    for mask_pair in mask_list:
        masked_image_list.append([image_gray*mask_pair[0], image_gray*mask_pair[1]])
    
def calculate_intensity_vector():
    intensity_vector = []
    intensity_vector.append(np.sum(image_gray*mask_pair[0])-np.sum(image_gray*mask_pair[1]))
    
def reconstruct_image():
    pass

# end1 = time.time()

# start2 = time.time()

# masked_image_list = []
# intensity_vector = []

# for mask_pair in mask_list:
	# masked_image_list.append([image_gray*mask_pair[0], image_gray*mask_pair[1]])
	# intensity_vector.append(np.sum(image_gray*mask_pair[0])-np.sum(image_gray*mask_pair[1]))
	
# end2 = time.time()

# start3 = time.time()

#hadamard_matrix_small = np.array(hadamard(int((N**2 * M))))

#hadamard_matrix_small_padded = np.zeros((N**2,N**2))
#hadamard_matrix_small_padded[0:hadamard_matrix_small.shape[0], 0:hadamard_matrix_small.shape[1]] = hadamard_matrix_small

#intensity_vector = np.append(intensity_vector, [0]*int(N**2-N**2*M))

# # zastąpienie K pomiarów z listy zerami
# K = int(N**2 - (N**2 * M))
# intensity_vector = intensity_vector[: len(intensity_vector) - K]
# intensity_vector.extend([0] * K)

# # x = H'y, ale H = H' (własność macierzy Hadamarda), więc x = Hy -> pozwala nie używać IFWHT
# result_pre = hadamard_matrix.dot(intensity_vector)

# print(result_pre.shape)

# result_final = np.reshape(result_pre, (N,N))
# #result_final = np.array(eng.ifwht(matlab.double(result_pre.tolist())))

# result_final *= (1.0/result_final.max())

# end3 = time.time()

# print("\nCzas generacji masek: " + str(end1-start1))
# print("\nCzas modulacji: " + str(end2-start2))
# print("\nCzas rekonstrukcji: " + str(end3-start3))

# MSE = mean_squared_error(image_gray, result_final)
# PSNR = 10*math.log10(image_gray.max()**2 / MSE)

# print("\nMSE: " + str(MSE))
# print("PSNR: " + str(PSNR) + "\n")

# show_images([image_gray, hadamard_matrix, result_final])
	
# sys.exit()