# system modules
import sys, os, time, random

# helper functions, mainly IO
import auxiliary_functions as aux

# masking and reconstruction
import fourier_module as fourier
## still WIP!
import hadamard_module as hadamard

# GUI
import PySimpleGUI as sg

# math
import numpy as np
import matplotlib.pyplot as plt

# connectivity
#import owon_get_data as owon

import arduino_control as arcon

dev = None

# directory locations
ground_truths_directory = "./GT/"
patterns_directory = "./PATTERNS/"
gallery_directory = "./GALLERY/"

# check if directories exist and if not - create them
if os.path.exists(patterns_directory) is False:
	os.mkdir(patterns_directory)
if os.path.exists(ground_truths_directory) is False:
	os.mkdir(ground_truths_directory)
if os.path.exists(gallery_directory) is False:
	os.mkdir(gallery_directory)

# initial reconstruction parameters
scale = 1
resolution = 32

# TODO - add controls for mode and threshold_mode on GUI level
mode = "lowpass"
# 0 - no threshold
# 1 - 4 - global, local and adaptive thresholding options
threshold_mode = 0

# fourier pattern generation parameters
# TODO - add controls for parameters on GUI level
A = 0.5
B = 0.5

# initial empty image and pattern list variables
image = None
patterns = None

intensity_vector = []

# Graphical theme for pysimplegui interface
sg.theme('LightGreen2')

# main window GUI definition
main_control_column = [
	[
		sg.Button("Reconstruct", key="-RECONSTRUCT-", disabled=True),
		sg.VSeparator(),
		sg.Button("Reconstruct/Real", key="-RECONSTRUCT_REAL-", disabled=False),
		sg.VSeparator(),
		sg.Button("Generate patterns", key="-GENERATE_PATTERNS-"),
		sg.VSeparator(),
		sg.Button("Export patterns", key="-EXPORT_PATTERNS-"),
		sg.Checkbox("PNG/BMP export mode", key="-EXPORT_MODE-", default=False),
		sg.VSeparator(),
		sg.Button("Load patterns", key="-LOAD_PATTERNS-"),
		sg.VSeparator(),
		sg.Button("Load image", key="-LOAD_IMG-"),
	],
	
	[
		sg.Checkbox("Fourier method", key="-FOURIER-", default=True),
	],
	
	[
		sg.Text("Normalization mode: ", size =(10, 1)), sg.InputText(size=(3, 1), key="-NORM_MODE-"),
	],
	
	[
		sg.Checkbox("Hadamard method", key="-HADAMARD-", default=False),
	],
	
	[
		sg.Text("Set compressive sensing factor:"),
	],
	
	[
		sg.Text("Factor:", size =(8, 1)), sg.InputText(size=(6, 1), key="-FACTOR-"),
	],
	
	[
		sg.Text("Set desired reconstruction resolution N (used as NxN):"),
	],
	
	[
		sg.Text("Resolution:", size =(8, 1)), sg.InputText(size=(6, 1), key="-RESOLUTION-"),
	],
	
	[
		sg.Text("Thresh. mode:", size=(10, 1)), sg.InputText(size=(6, 1), key="-THRESHOLD_MODE-"),
	],
	
]

menu_layout = [
	[
		sg.Column(main_control_column),
	],
	
	[
		sg.HSeparator(),
	],
	
	[
		sg.Text("Current loaded image: "),
		sg.Text("None", size=(15, 1), key="-CURRENT_IMAGE_NAME-"),
	],
	
	[
		sg.HSeparator(),
	],
	
	[
		sg.Text("Status: "),
		sg.Text("", size=(40, 1), key="-STATUS-"),
	],
	
	[
		sg.HSeparator(),
	],
	
	[
		sg.Button("Change parameters (clears patterns!)", key="-CHANGE_VALS-"),
		sg.Button("Clear pattern dir", key="-CLEAR_PATTERNS-"),
		sg.Button("Exit"),
	],
	
	[
		sg.HSeparator(),
	],
	
	[
		sg.Button("Remote control", key="-REMOTE_CONTROL-"),
	],
]

# main window initialization
main_window = sg.Window("Single Pixel Imaging Simulator - SPIS v0.2", menu_layout, finalize=True)
#main_window.maximize()
main_window.FindElement("-STATUS-").Update("Idle.")

# TODO: 
# - add checking if patterns are None at the end of the main loop
# - Change ouput in terminal to output in window/windows of the GUI
#       one window layout for all notifications?
#       one window for each part (reconstruction, pattern gen with export/import?)
# - proper checking if patterns and image are present, == None is not optimal! (ambiguity error when calling it on a non-None element)
# implement hadamard module functionality - needs to work/recognize pattern types in dirs
while True:
	# IMPORTANT!
	# re-call layouts every loop iteration to avoid errors during reopening windows!
	# the same layouts (as in 'same variables') cannot be reused in pysimplegui!

	gallery_layout = [
		[
			sg.Text(key="-IMAGE_NAME-"),
			sg.Image(key="-IMAGE-"),
			sg.Button("Left", key="-LEFT-"),
			sg.Button("Right", key="-RIGHT-"),
			sg.Button("Exit")
		]
	]
	
	image_loader_layout = [
		[
			sg.Text(key="-IMAGE_NAME-"),
			sg.Image(key="-IMAGE-"),
			sg.Button("Left", key="-LEFT-"),
			sg.Button("Right", key="-RIGHT-"),
			sg.Button("Load!", key="-LOAD_SEL_IMG-"),
		]
	]
	
	remote_control_layout = [
		[
			sg.Button("Connect to BeagleBoard", key="-BEAGLE_CONNECT-"),
		],
		
		[
			sg.Text("Password:", size =(8, 1)), sg.InputText(size=(10, 1), key="-PASSWORD-"),
		],
		
		[
			sg.Checkbox("Connection status: ", default=False, disabled=True, key="-BEAGLE_STATUS-"),
		],
			
		[
			sg.HSeparator(),
		],
		
		[
			sg.Button("Connect to Arduino", key="-ARD_CONNECT-"),
		],
		
		[
			sg.Text("Port:", size =(8, 1)), sg.InputText(size=(10, 1), key="-ARD_PORT-"),
		],
		
		[
			sg.Checkbox("Connection status: ", default=False, disabled=True, key="-ARD_STATUS-"),
		],
			
		[
			sg.HSeparator(),
		],
		
			
		[
			sg.Button("Connect to DLPLCRDC4422EVM", key="-DLP_EVM_CONNECT-"),
		],
		
		[
			sg.Checkbox("Connection status: ", default=False, disabled=True, key="-DLP_EVM_STATUS-"),
		],
	]
	
	# Beagleboard control screen - after remote connection
	# maybe merge those two?
	
	# Control scheme:
	#	- send pattern subset
	#	- display patterns and acquire measurment
	#		- display pattern with trigger
	#		- measure intensity on oscilloscope with owon_get_data.py (either on BBB or PC)
	#		- set trigger to high, via file edits in paramiko/ssh
	#	- delete patterns on BBB
	#	- repeat

	event, values = main_window.read()
	
	# DEBUG
	#print(values)
	#print(event)
	#print(image)
	
	# Exit event
	if event == "Exit" or event == sg.WIN_CLOSED:
		break
	
	if event == "-RECONSTRUCT-":
		image_resized = aux.resize_image(image, resolution)
		
		if patterns == None:
			print("No patterns! Please generate or add patterns to reconstruct the image.")
			main_window.FindElement("-STATUS-").Update("No patterns! Please generate or add patterns to reconstruct the image.")
			
		else:
			print("Starting reconstruction...")
			main_window.FindElement("-STATUS-").Update("Starting reconstruction...")
			
			if patterns[0][0].size == image_resized.size:
				reconstructed_image, fourier_spectrum_2D_padded = fourier.reconstruct_image(resolution, scale, fourier.calculate_fourier_coeffs(fourier.mask_image(image_resized, patterns)), "lowpass", 0)
				
				print("Reconstruction done.")
				main_window.FindElement("-STATUS-").Update("Reconstruction done.")
				
				# DEBUG Fourier plane
				aux.save_image(np.real(fourier_spectrum_2D_padded), "fourier_padded", "")
				
				#aux.save_image(gallery_directory, reconstructed_image, "rec_img")
				aux.show_images([image, image_resized, np.real(fourier_spectrum_2D_padded), np.real(reconstructed_image)], 1)
			
			else:
				print("Pattern size is different from the selected resolution!")
				main_window.FindElement("-STATUS-").Update("Reconstruction error - wrong pattern size!")
	
	elif event == "-RECONSTRUCT_REAL-":
		# DEBUG when commented
		if len(intensity_coeff_list) < 1:
			print("No measurements!")
			main_window.FindElement("-STATUS-").Update("No measurements!")
	
		else:
			print("Starting reconstruction...")
			main_window.FindElement("-STATUS-").Update("Starting reconstruction...")
			
			norm_mode = int(values["-NORM_MODE-"])
			
			reconstructed_image, fourier_spectrum_2D_padded = fourier.reconstruct_image(resolution, scale, intensity_coeff_list, "real", norm_mode)

			print("Reconstruction done.")
			main_window.FindElement("-STATUS-").Update("Reconstruction done.")
				
			# DEBUG Fourier plane
			aux.save_image_complex(np.real(fourier_spectrum_2D_padded), "./GALLERY/fourier_padded", "")
				
			#aux.save_image(gallery_directory, reconstructed_image, "rec_img")
			#aux.show_images([image, np.real(fourier_spectrum_2D_padded), np.real(reconstructed_image)], 1)
			
	elif event == "-GENERATE_PATTERNS-":
			
		print("Generating patterns...")
		main_window.FindElement("-STATUS-").Update("Generating patterns...")
		
		if values["-FOURIER-"] is True and values["-HADAMARD-"] is True or values["-FOURIER-"] is False and values["-HADAMARD-"] is False:
			print("Please choose only one type of patterns!")
			main_window.FindElement("-STATUS-").Update("Please choose only one type of patterns!")
		
		elif values["-FOURIER-"] is True and values["-HADAMARD-"] is False:
			patterns = fourier.generate_patterns(resolution, scale, A, B, threshold_mode, mode, patterns_directory)
			print("Fourier patterns generated to memory.")
			main_window.FindElement("-STATUS-").Update("Fourier patterns generated to memory.")
		
		elif values["-FOURIER-"] is False and values["-HADAMARD-"] is True:
			patterns = hadamard.generate_patterns(resolution)
			print("Hadamard patterns generated to memory.")
			main_window.FindElement("-STATUS-").Update("Hadamard patterns generated to memory.")

		if image is not None:
			main_window.FindElement("-RECONSTRUCT-").Update(disabled=False)
	
	elif event == "-EXPORT_PATTERNS-":
		# TODO: add mode selection to export patterns as .png
		if patterns != None:
			if len(os.listdir(patterns_directory)) == 0:
				print("Exporting patterns...")
				main_window.FindElement("-STATUS-").Update("Exporting patterns in PNG mode: " + str(values["-EXPORT_MODE-"]))
				
				aux.save_list_of_lists(patterns, patterns_directory, values["-EXPORT_MODE-"], resolution)
				
				print("Patterns exported to patterns directory.")
				main_window.FindElement("-STATUS-").Update("Patterns exported to patterns directory.")
			else:
				print("Pattern directory is already filled! Clear patterns before saving.")
				main_window.FindElement("-STATUS-").Update("Pattern directory is already filled! Clear patterns before saving.")
		else:
			print("No patterns to export!")
			main_window.FindElement("-STATUS-").Update("No patterns to export!")

	# TODO
	# Not reconstructing properly! Need to check export/import settings for .npy files
	elif event == "-LOAD_PATTERNS-":
		if len(os.listdir(patterns_directory)) != 0:
			print("Overwriting patterns in memory...")
			main_window.FindElement("-STATUS-").Update("Overwriting patterns in memory...")
			
			if patterns != None:
				print("Overwriting patterns in memory...")
				main_window.FindElement("-STATUS-").Update("Overwriting patterns in memory...")
			
			patterns = aux.load_list_of_lists(patterns_directory, 1)
			
			main_window.FindElement("-STATUS-").Update("Done loading patterns!")
			
			if patterns != None and image != None:
				main_window.FindElement("-RECONSTRUCT-").Update(disabled=False)
				
		else:
			print("Can't load patterns, pattern directory is empty!")
			main_window.FindElement("-STATUS-").Update("Can't load patterns, pattern directory is empty!")

	elif event == "-LOAD_IMG-":
		image_loader_window = sg.Window("LOAD", image_loader_layout, finalize=True)
		
		image_num = 0
		
		file_list = os.listdir(ground_truths_directory)
		
		while True:
			file_list = os.listdir(ground_truths_directory)
			
			if file_list != []:
				current_image = file_list[image_num]
				image_loader_window["-IMAGE-"].update(ground_truths_directory + current_image)
				image_loader_window["-IMAGE_NAME-"].update(current_image)
			
			load_event, load_values = image_loader_window.read()
			
			if load_event == "-LOAD_SEL_IMG-":
				image = aux.load_image(ground_truths_directory + current_image)
				
				print("\nImage " + str(current_image) + " loaded.\n")
				main_window.FindElement("-STATUS-").Update("Image " + str(current_image) + " loaded.")
				
				if patterns != None:
					main_window.FindElement("-RECONSTRUCT-").Update(disabled=False)
					
				main_window['-CURRENT_IMAGE_NAME-'].Update(current_image)
				break
			
			elif load_event == sg.WIN_CLOSED:
				break
			 
			elif load_event == "-LEFT-":
				if image_num > 0:
					image_num-=1
				
			elif load_event == "-RIGHT-":
				if image_num < len(file_list)-1:
					image_num+=1

		image_loader_window.close()
	
	elif event == "-CLEAR_PATTERNS-":
		try:
			print("Clearing patterns in pattern directory...")
			main_window.FindElement("-STATUS-").Update("Clearing patterns in pattern directory...")
			
			aux.clear_directory(patterns_directory)
			
			print("Patterns cleared from directory.")
			main_window.FindElement("-STATUS-").Update("Patterns cleared from directory.")
			
		except PermissionError:
			print("Error removing patterns! Please clear the folder manually or wait for a few minutes before retrying.")
			main_window.FindElement("-STATUS-").Update("Error removing patterns! Please clear the folder manually or wait for a few minutes before retrying.")
		
	elif event == "-CHANGE_VALS-":
		print("Changing values...")
		main_window.FindElement("-STATUS-").Update("Changing values...")
		
		if values["-FACTOR-"] is not None and values["-FACTOR-"] is not '':
			scale = float(values["-FACTOR-"])
		if values["-RESOLUTION-"] is not None and values["-RESOLUTION-"] is not '':
			resolution = int(values["-RESOLUTION-"])
		if values["-THRESHOLD_MODE-"] is not None and values["-THRESHOLD_MODE-"] is not '':
			threshold_mode = int(values["-THRESHOLD_MODE-"])
		   
		# TODO -> pass info or reset patterns so that the reconstruction doesn't crash on a different resolution
		main_window.FindElement("-RECONSTRUCT-").Update(disabled=True)
		patterns = None
		
		print("Parameter values changed.")
		main_window.FindElement("-STATUS-").Update("Parameter values changed.")
	
	# Remote system control
	elif event == "-REMOTE_CONTROL-":
		# remote control window initialization
		remote_window = sg.Window("Remote control", remote_control_layout, finalize=True)
		
		# ssh client from paramiko
		client = None
		sub_client = None
		
		# arduino variable
		# declared in the begininng to allow serial connection closing outside of loop
		#dev = None
		
		remote_window.FindElement("-BEAGLE_STATUS-").Update(False)
		
		while True:
			remote_event, remote_values = remote_window.read()
			
			# DEBUG
			#print(remote_values)
			
			# Exit event
			if remote_event == "Exit" or remote_event == sg.WIN_CLOSED:
				# cleanly close existing ssh connection when the loop is broken
				
				# alternative
				#if remote_values["-BEAGLE_STATUS-"] is True and client != None:
				
				if client is not None:
					aux.close_ssh(client)
				if sub_client is not None:
					aux.close_ssh(client)
				break
				
			# connect to BeagleBone controller for DLP2000 projector control
			if remote_event == "-BEAGLE_CONNECT-":
				if remote_values["-BEAGLE_STATUS-"] is False:
					if remote_values["-PASSWORD-"] is not '':
						# closing the client after each command might fix some further issues
						client = aux.connect_ssh(remote_values["-PASSWORD-"])
						print("Starting connection...")
					
					else:
						print("No password provided!")
				
				# if connected to BBB
				## DEBUG: ==
				# NORMAL: !=
				if client != None:
					# layout declaration oved to internal section to avoid crashes when calling window for the second time
					BBB_layout = [
									[
										sg.Button("Send and display patterns", key="-SEND_AND_DISPLAY_PATTERNS-"),
									],
									
									[
										sg.Checkbox("Use automatic trigger to display patterns", default=False, disabled=False, key="-TRIGGER_MODE-"),
									],
									
									[
										sg.Text("Pattern batch size:", size =(20, 1)), sg.InputText(size=(8, 1), key="-PATTERN_BATCH_SIZE-"),
									],
									
									[
										sg.Text("Display framerate (without trigger):", size =(25, 1)), sg.InputText(size=(8, 1), key="-FRAMERATE-"),
									],
					]
				
					print("Connected!")
					remote_window.FindElement("-BEAGLE_STATUS-").Update(True)
					
					patterns_on_BBB = False
					
					trigger_mode = False
					
					BBB_window = sg.Window("BBB Control", BBB_layout, finalize=True)
					
					while True:
						BBB_event, BBB_values = BBB_window.read()
						
						# returns NoneType, need to check for issues
						# temporary workaround with try/except
						try:
							trigger_mode = BBB_values["-TRIGGER_MODE-"]
						except TypeError:
							print("DEBUG: Trigger object error omitted...")
						
						if BBB_event == "Exit" or BBB_event == sg.WIN_CLOSED:
							break
						
						elif BBB_event == "-SEND_AND_DISPLAY_PATTERNS-":
							# check if there already are patterns on the BBB
							#output = aux.execute_remote_command(client, 'find /home/debian/Desktop/DLP_Control/structured_light;./pattern_disp -i')
						
							# TODO - add loop that will display all patterns in subsets
							
							pattern_list = os.listdir(patterns_directory)
							
							# if there are files in the pattern directory
							if len(pattern_list) != 0:
								# pattern starting number
								p_num = 0
								# pattern batch size - amount of patterns that will be sent to BBB
								# Check if it works for large pattern sets
								p_batch_size = int(BBB_values["-PATTERN_BATCH_SIZE-"])
								
								# while the pattern number p_num has not surpassed the pattern amount
								while p_num < len(os.listdir(patterns_directory)):
									partial_pattern_dir_list = []
									
									# select patterns that match numbers that are currently sent/measured
									# iterates over all images - might be slow!
									# alternative - explicitly select images via their numbers
									for image in pattern_list:
										# Works only up to 999 patterns!
										if image[1] == '_':
											if p_num <= int(image[0]) < p_num + p_batch_size:
												partial_pattern_dir_list.append(image)
												
										elif image[2] == '_':
											if p_num <= int(image[0:2]) < p_num + p_batch_size:
												partial_pattern_dir_list.append(image)
												
										elif image[3] == '_':
											if p_num <= int(image[0:3]) < p_num + p_batch_size:
												partial_pattern_dir_list.append(image)
									
									# DEBUG
									print("Currently batched patterns:")
									print(partial_pattern_dir_list)
									print("\n")
									
									# transfer selected patterns to BBB
									
									# check zeroing!
									temp_number = 0
									
									# quick&dirty override that takes care of superfluous loop
									# check if the pattern list is empty
									if partial_pattern_dir_list:
										# open sftp client on existing connection
										ftp_client = client.open_sftp()
										if ftp_client != None:
											print("SFTP connection opened!")
										
										for pattern_name in partial_pattern_dir_list:
											print("Uploading pattern: " + pattern_name)
											ftp_client.put("./PATTERNS/" + pattern_name, "/home/debian/Desktop/DLP_Control/structured_light/" + str(temp_number) + ".bmp")
											temp_number += 1
											
										print("Pattern subset sent!")
								
										# close client after transfer
										ftp_client.close()
								
									else:
										print("No patterns in batched list, overriding...")
								
									# move on to next pattern set
									p_num += p_batch_size
									
									# TODO
									# display patterns, according to mode
									if trigger_mode is True:
										# temporary override that ignores the additional loops
										if partial_pattern_dir_list:
											sub_client = aux.connect_ssh(remote_values["-PASSWORD-"])
											
											if sub_client is not None:
												print("GPIO subclient connected!")
											
											# check if the lines below should be in the if above
											
											output = aux.execute_remote_command(client, 'cd /home/debian/Desktop/DLP_Control/structured_light && ./pattern_disp -i')
											
											# COMMENT OUT FOR DEBUG - The program hangs on readlines() - check!
											# if commented, the ssh client hangs and ftp_client.close() returns Administratively Prohibited error
											#print(output[1].readlines())
											#print(output[2].readlines())
											
											print("Starting triggered display...")
											
											# show first pattern
											#output = aux.execute_remote_command(sub_client, 'echo high > /sys/class/gpio/gpio115/direction && sleep .05 && echo low > /sys/class/gpio/gpio115/direction')
											#print(output[1].readlines())
											#print(output[2].readlines())
											
											# BUG - the last pattern is not triggered and the process doesn't close - check loop arguments! -> added TEMPORARY +1 to loops, check if it works!
											# BUG - tearing of some patterns - check if its CPU or code related! -> most likely CPU, check display driver support
											# BUG - one measurment too many! - check loops
											
											#output = aux.execute_remote_command(sub_client, 'echo high > /sys/class/gpio/gpio115/direction && sleep .01 && echo low > /sys/class/gpio/gpio115/direction')
											#print(output[1].readlines())
											#print(output[2].readlines())
											
											# most likely required to allow BBB to initialize the display program
											# without this delay the pattern are sometimes not properly triggered and tend to lag 1 pattern behind
											time.sleep(0.5)
											
											#output = aux.execute_remote_command(sub_client, 'echo high > /sys/class/gpio/gpio115/direction && sleep .01 && echo low > /sys/class/gpio/gpio115/direction')
											#print(output[1].readlines())
											#print(output[2].readlines())
											
											# trigger the display of concurrent patterns
											# temporary range from 1 to check if it helps reduce measurments
											for remote_p_num in range(0, p_batch_size*3):
												if remote_p_num == 0:
													# start the display
													output = aux.execute_remote_command(sub_client, 'echo high > /sys/class/gpio/gpio115/direction && sleep .01 && echo low > /sys/class/gpio/gpio115/direction')
													print(output[1].readlines())
													print(output[2].readlines())
											
												# TODO - add GUI-side control of command value
												
												# single-shot
												#command = b'n'
												
												# 10x averaging 
												command = b'a'
												
												# placeholder for a detector other than the photoresistor
												#command = b'c'
											
												time.sleep(0.1)

												### stupid solution and it doesn't work, check for something better
												# might be an issue with triggering/paramiko?
												# switch patterns "inside" batch
												#if remote_p_num < p_batch_size*3-1:
												#    # echo taken from:
												#    # https://developer.toradex.com/knowledge-base/gpio-linux#To_directly_force_a_GPIO_to_output_and_set_its_initial_value_eg_glitchfree_operation
												#    output = aux.execute_remote_command(sub_client, 'echo high > /sys/class/gpio/gpio115/direction && sleep .1 && echo low > /sys/class/gpio/gpio115/direction')
												#    print(output[1].readlines())
												#    print(output[2].readlines())
												
												if remote_values["-ARD_STATUS-"] is True:
													#output = aux.execute_remote_command(sub_client, 'echo high > /sys/class/gpio/gpio115/direction && sleep .1 && echo low > /sys/class/gpio/gpio115/direction')
													#print(output[1].readlines())
													#print(output[2].readlines())
												
													# get intensity data from single-pixel detector->arduino ADC
													intensity_vector.append(arcon.get_value(dev, command))
													
													output = aux.execute_remote_command(sub_client, 'echo high > /sys/class/gpio/gpio115/direction && sleep .01 && echo low > /sys/class/gpio/gpio115/direction')
													print(output[1].readlines())
													print(output[2].readlines())
												else:
													print("Arduino not connected!")
													
												
												
												# end pattern display after batch, AFTER measurement
												#if remote_p_num == p_batch_size*3-1:
													# echo taken from:
													# https://developer.toradex.com/knowledge-base/gpio-linux#To_directly_force_a_GPIO_to_output_and_set_its_initial_value_eg_glitchfree_operation
												#	output = aux.execute_remote_command(sub_client, 'echo high > /sys/class/gpio/gpio115/direction && sleep .1 && echo low > /sys/class/gpio/gpio115/direction')
												#	print(output[1].readlines())
												#	print(output[2].readlines())
													
												print(intensity_vector[-1])
												
												time.sleep(0.1)
											
											# remove all images from dir
											output = aux.execute_remote_command(sub_client, 'cd /home/debian/Desktop/DLP_Control/structured_light && rm *.bmp')
											print(output[1].readlines())
											print(output[2].readlines())
												
											# DEBUG
											# trigger the pattern display one more time - if it lagged this will end it properly
											# currently no way to check if the trigger got stuck/delayed -> this solves the continuity problem, with the drawback of having one false batch measurement
											#output = aux.execute_remote_command(sub_client, 'echo high > /sys/class/gpio/gpio115/direction && sleep .01 && echo low > /sys/class/gpio/gpio115/direction')
											#print(output[1].readlines())
											#print(output[2].readlines())
												
											aux.close_ssh(sub_client)
										
									else:
										output = aux.execute_remote_command(client, 'cd /home/debian/Desktop/DLP_Control/structured_light && ./pattern_disp -k ' + BBB_values["-FRAMERATE-"])
										print(output[1].readlines())
										print(output[2].readlines())
										
								# DEBUG
								print("\nPomiar: \n")
								print(intensity_vector)
								print("\nIlość punktów pomiarowych: ")
								print(len(intensity_vector))
								
								# calculate coefficients based on the measured intensities
								intensity_coeff_list = []
								
								for i in range(0, len(intensity_vector), 3):
									intensity_coeff_list.append((2*intensity_vector[i] - intensity_vector[i+1] - intensity_vector[i+2]) + np.sqrt(3)*1j*(intensity_vector[i+1] - intensity_vector[i+2]))

								# DEBUG
								print("\nWyznaczone współczynniki zespolone: \n")
								print(intensity_coeff_list)
								print("\nLiczba wyznaczonych współczynników: \n")
								print(len(intensity_coeff_list))
								
							else:
								print("No patterns to send in directory!")
				else:
					print("No connection to BBB!")
						
			# placeholder
			# connect to DLP_EVM for DMD modulation
			elif remote_event == "-DLP_EVM_CONNECT-":
				# TODO
				pass
			
			# TODO
			# connect to oscilloscope for measurement vector acquisition
			elif remote_event == "-ARD_CONNECT-":
				# TODO
				# initial connection
				# check if it's possible to see if it is connected (osc_device != None ???)
				#osc_device = owon.connect()
				#if osc_device is not None:
				#	print("Connected to oscilloscope!")
				#pass
				
				arduino_port = remote_values["-ARD_PORT-"]
				
				# if not filled, default to COM7
				if arduino_port is None:
					arduino_port = 'COM7'
				
				dev = arcon.init_serial(arduino_port, 9600, 0)
				if dev != None:
					print("Arduino connected!")
					remote_window.FindElement("-ARD_STATUS-").Update(True)
					
				
# disconnect arduino - TODO - change to button inside menu
arcon.close_serial(dev)
				
# clean up after the program
main_window.close()

# end the program
sys.exit()