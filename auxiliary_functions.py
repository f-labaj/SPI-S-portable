import os, time
import glob

from numpy import save, load
import numpy as np
import matplotlib.pyplot as plt

from skimage import io
from skimage import color
from skimage import img_as_bool
from skimage.transform import resize

import scipy.misc

from PIL import Image

import paramiko

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
				el_resized_square = np.resize(el, (360,360))
				el_resized_padded = np.pad(el_resized_square, ((0,0), (140,140)), 'constant', constant_values=0)
				img = Image.fromarray((el_resized_padded * 255 ))
				# change bit depth to 24-bit True Color - the only format accepted by DLP2000 default display software
				img_24 = img.convert("RGB")
				img_24.save(directory + str(i) + '_' + str(j) + '.bmp')
				j += 1
			i += 1
		
		print("Done saving patterns!")

	else:
		print("Export mode error!")

    # # save as .npy for efficient binary IO
    # if mode == 1:
        # i = 0
        # for lst in list_of_lists:
            # j = 0
            # for el in lst:
                # save(directory + 'name_' + str(i) + '_' + str(j) + '.npy', el, allow_pickle=False)
                # j += 1
            # i += 1
		
        # print("Done saving patterns!")
        
    # # Currently not usable
    # # save as .png for viewing
    # elif mode == 2:
        # i = 0
        # for lst in list_of_lists:
            # j = 0
            # for el in lst:
                # save(directory + 'name_' + str(i) + '_' + str(j) + '.png', el, allow_pickle=False)
                # j += 1
            # i += 1
           
        # print("Done saving patterns!")   
           
    # # save as .png in 1920x1080 for DMD display
    # elif mode == 3:
        # i = 0
        # for lst in list_of_lists:
            # j = 0
            # for el in lst:
                # Image.fromarray(np.resize(el, (1280,1280))).save(directory + 'dmd_name_' + str(i) + '_' + str(j) + '.png')
                # j += 1
            # i += 1
        # print("Done saving patterns!")
        
    # else:
        # print("Export mode error!")
    
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
	# change bit depth to 24-bit True Color - the only format accepted by DLP2000 default display software
	img_24 = img.convert("RGB")
	img_24.save(str(directory) + str(img_name) + '.bmp')

def load_image(filename):
	image = io.imread(filename)
	
	image_gray = color.rgb2gray(image)

	return image_gray
    
def resize_image(image, resolution):
    N = resolution
    image_resized = resize(image, (N, N))
    
    return image_resized

# funkcja do wyświetlania wielu obrazów naraz
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
    assert((titles is None)or (len(images) == len(titles)))
    n_images = len(images)
    if titles is None: titles = ['Image (%d)' % i for i in range(1,n_images + 1)]
    fig = plt.figure()
    for n, (image, title) in enumerate(zip(images, titles)):
        a = fig.add_subplot(cols, np.ceil(n_images/float(cols)), n + 1)
        if image.ndim == 2:
            plt.summer()
        plt.imshow(image)
        a.set_title(title)
    fig.set_size_inches(np.array(fig.get_size_inches()) * n_images)
    plt.show()