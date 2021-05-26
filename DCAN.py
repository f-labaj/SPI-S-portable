import os, sys

#def generate_dataset(dataset_size)


# https://medium.com/analytics-vidhya/building-a-convolutional-autoencoder-using-keras-using-conv2dtranspose-ca403c8d144e
os.environ['KERAS_BACKEND'] = 'tensorflow'
from keras.preprocessing.image import ImageDataGenerator

gen = ImageDataGenerator()

train_im = ImageDataGenerator(
								rescale = 1./255, 
								shear_range=0.2, 
								horizontal_flip=False
								)

def train_images():
	train_generator = train_im.flow_from_directory(
													'./TRAINING_DATA/',
													target_size=(32, 32),
													color_mode='grayscale',
													batch_size=100,
													shuffle=True,
													class_mode='categorical'
													)
	
	x = train_generator
	return x[0][0], x[0][1]

import tensorflow
import keras
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from keras.datasets import mnist
from keras.models import Model, Sequential
from keras.layers import Dense, Conv2D, Dropout, BatchNormalization, Input, Reshape, Flatten, Conv2DTranspose, MaxPooling2D, UpSampling2D
from keras.layers.advanced_activations import LeakyReLU
from keras.optimizers import Adam

# https://keras.io/api/layers/regularizers/
# should force the encoding layer to lean towards binary modulation of the training images
# 
#def binary_regularizer(x):
#	return 1e-3 * tf.

# encoder
inp = Input((32, 32, 1))
e = Conv2D(32, (3, 3), activity_regularizer=activation='relu')(inp)
e = Conv2D(64, (3, 3), activation='relu')(e)
e = Conv2D(64, (3, 3), activation='relu')(e)
l = Flatten()(e)
l = Dense(64, activation='softmax')(l)

# decoder
d = Reshape((8, 8, 1))(l)
d = Conv2DTranspose(64, (3, 3), strides=2, activation='relu', padding='same')(d)
d = Conv2DTranspose(64, (3, 3), strides=2, activation='relu', padding='same')(d)
d = Conv2DTranspose(32, (3, 3), activation='relu', padding='same')(d)
decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(d)

# encoder
#inp = Input((32, 32, 1))
#e = Conv2D(32, (3, 3), activation='relu')(inp)
#e = MaxPooling2D((2, 2))(e)
#e = Conv2D(64, (3, 3), activation='relu')(e)
#e = MaxPooling2D((2, 2))(e)
#e = Conv2D(64, (3, 3), activation='relu')(e)
#l = Flatten()(e)
#l = Dense(64, activation='softmax')(l)

# decoder
#d = Reshape((8, 8, 1))(l)
#d = Conv2DTranspose(64, (3, 3), strides=2, activation='relu', padding='same')(d)
#d = BatchNormalization()(d)
#d = Conv2DTranspose(64, (3, 3), strides=2, activation='relu', padding='same')(d)
#d = BatchNormalization()(d)
#d = Conv2DTranspose(32, (3, 3), activation='relu', padding='same')(d)
#decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(d)

ae = Model(inp, decoded)
ae.summary()

sys.exit()

#(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
#train_images = train_images.reshape((60000, 28, 28, 1))
#test_images = test_images.reshape((10000, 28, 28, 1))

# Normalize pixel values to be between 0 and 1
#train_images, test_images = train_images / 255.0, test_images / 255.0

# compile it using adam optimizer
ae.compile(optimizer="adam", loss="mse")
#Train it by providing training images
ae.fit(train_images, train_images, epochs=2)

#IF you want to save the model
#model_json = ae.to_json()
#with open("model_tex.json", "w") as json_file:
#    json_file.write(model_json)

#ae.save_weights("model_tex.h5")
#print("Saved model")

prediction = ae.predict(train_images, verbose=1, batch_size=100)# you can now display an image to see it is reconstructed well
x = prediction[0].reshape(28,28)
plt.imshow(x)
plt.show()