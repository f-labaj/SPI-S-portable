import tensorflow as tf
from tensorflow.keras import layers

import numpy as np
import matplotlib.pyplot as plt

import sys, os

import keras.utils.vis_utils
from importlib import reload
reload(keras.utils.vis_utils)

from keras.utils.vis_utils import plot_model

import tensorflow.keras.backend as K

def binary_reg(weight_matrix):
   return 0.01 * tf.math.reduce_sum(tf.math.square(weight_matrix))

def euclidean_distance_loss(y_true, y_pred):
    """
    Euclidean distance loss
    https://en.wikipedia.org/wiki/Euclidean_distance
    :param y_true: TensorFlow/Theano tensor
    :param y_pred: TensorFlow/Theano tensor of the same shape as y_true
    :return: float
    """
    return K.sqrt(K.sum(K.square(y_pred - y_true), axis=-1))

def SPI(image, pattern):
	masked_image = image * pattern
	measurement_vector = tf.reduce_sum(masked_image, [1, 2])
	
	return measurement_vector

def SPI_2(images, masking_patterns):
	temp_vector = tf.zeros([0, 300])
	measurement_vector = tf.zeros([20, 300])

	for image in images:
			masked_image = image * masking_patterns
			intensity = tf.reduce_sum(masked_image, [1, 2])
			measurement_vector = tf.concat([temp_vector, intensity], axis=0)
	
	return measurement_vector

def generator(name):
	inp = tf.keras.Input(shape=(28, 28, 1))
	
	x = layers.Flatten()(inp)
	
	x = layers.Dense(7*7*1200, use_bias=False, input_shape=(784,))(x)
	x = layers.BatchNormalization()(x)
	x = layers.LeakyReLU()(x)
	
	x = layers.Reshape((7, 7, 1200))(x)

	x = layers.Conv2DTranspose(900, (5, 5), strides=(1, 1), padding='same', use_bias=False)(x)
	x = layers.BatchNormalization()(x)
	x = layers.LeakyReLU()(x)
	
	x = layers.Conv2DTranspose(600, (5, 5), strides=(2, 2), padding='same', use_bias=False)(x)
	x = layers.BatchNormalization()(x)
	x = layers.LeakyReLU()(x)

	output = layers.Conv2DTranspose(300, (5, 5), strides=(2, 2), padding='same', use_bias=False, activation='tanh', activity_regularizer=binary_reg)(x)
	
	return tf.keras.Model(inp, output, name=name)
	
def reconstructor(name):
	inp = tf.keras.Input(shape=(300,))
	
	x = layers.Dense(28**2, activation='relu', input_shape=(300,))(inp)
	x = layers.Dense(28**2, activation='sigmoid')(x)
	
	output = layers.Reshape((28, 28, 1))(x)

	return tf.keras.Model(inp, output, name=name)

gen = generator("generator")
rec = reconstructor("reconstructor")

gen.summary()
rec.summary()

vector = SPI(gen.input, gen.output)
out = rec(vector)

full = tf.keras.Model(gen.input, out, name="full")
full.summary()

#sys.exit()

#plot_model(full, to_file="SPI.png", show_shapes=True, show_layer_names=True)

(x_train, _), (x_test, _) = tf.keras.datasets.mnist.load_data()

print(x_train.shape)
print(x_test.shape)

x_train = x_train.reshape(x_train.shape[0], 28, 28, 1).astype('float32') / 255
#x_train = (x_train - 127.5) / 127.5  # Normalize the images to [-1, 1]

x_test = x_test.reshape(x_test.shape[0], 28, 28, 1).astype('float32') / 255
#x_test = (x_test - 127.5) / 127.5  # Normalize the images to [-1, 1]

full.compile(
    loss=euclidean_distance_loss,
    optimizer=tf.keras.optimizers.Adam(),
    metrics=["accuracy"],
)

history = full.fit(x_train, x_train, batch_size=40, epochs=10, validation_split=0.2)

test_scores = full.evaluate(x_test, x_test, verbose=2)
print("Test loss:", test_scores[0])
print("Test accuracy:", test_scores[1])

gen.save("generator_model")
rec.save("reconstructor_model")

full.save("GANDCAN_model")

del gen
del rec
del full