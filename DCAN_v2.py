import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf

from tensorflow.keras import layers

from tensorflow.keras.datasets import mnist
from extra_keras_datasets import stl10

from tensorflow.keras.callbacks import TensorBoard

import tensorflow.keras.backend as K
from tensorflow.keras.optimizers import SGD

import sys

mask_modulation_num = 500
N = 28

#batch_size = 50

# convert rgb to grayscale, weighted(?)
def rgb2gray(rgb):
    return tf.expand_dims(np.dot(rgb[...,:3], [0.299, 0.587, 0.144]), axis=-1)
	
def resize(img, dim):
	return tf.image.resize(img, [dim, dim])

# calculate the measurement vector from masked images
def SPI(image):
	return tf.math.reduce_sum(image, [1, 2])
	
# custom regularizer that forces the masks to binarize
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
	
###

input_img = tf.keras.Input(shape=(N, N, 1))

# masking the image
# requires regularization towards -1 and 1 values

#encoded = layers.Conv2D(mask_modulation_num, 1, padding="same", activity_regularizer=binary_reg)(input_img)
#encoded = layers.Conv2D(mask_modulation_num, 1, padding="same", activation='tanh')(input_img)
#encoded = layers.Conv2D(mask_modulation_num, 1)(tf.expand_dims(input_img, axis=-1))

# changes dimensionality to width x height x mask_num

#encoded = layers.Conv2D(mask_modulation_num, 1)(input_img)

encoded = layers.Conv2D(mask_modulation_num, 1)(tf.signal.fft(input_img))

# dense layers with normalization to generate mask values
encoded = layers.Dense(mask_modulation_num)(encoded)

encoded = layers.LayerNormalization()(encoded)

# mask the images through multiplication
masked = layers.Multiply()([encoded, input_img])

# calculate the intensity vector
integrated = layers.Lambda(SPI)(masked)

#test_layer = layers.Reshape((N, N, 1))(integrated)

# + an additional reconstruction step?
#

# fully connected filter for image reconstruction

# N*N*mask_num from C. Higham pub.
#decoded = layers.Dense(N**2 * mask_modulation_num, activation='relu')(integrated)
decoded = layers.Dense(N**2, activation='relu')(integrated)

# reshaping the reconstruction
decoded = layers.Reshape((N, N, 1))(decoded)
decoded = layers.LayerNormalization()(decoded)

# # image superresolution
superres = layers.Conv2D(int(N/2), (9, 9), 1, activation='relu')(decoded)
#superres = layers.MaxPooling2D((2, 2))(superres)
superres = layers.Dropout(0.25)(superres)

superres = layers.LayerNormalization()(superres)

superres = layers.Conv2D(int(N/4), (1, 1), int(N/2), activation='relu')(superres)
#superres = layers.MaxPooling2D((2, 2))(superres)
superres = layers.Dropout(0.25)(superres)

superres = layers.LayerNormalization()(superres)

superres = layers.Conv2D(1, (5, 5), int(N/4), activation='relu', padding='same')(superres)
#superres = layers.MaxPooling2D((2, 2))(superres)
superres = layers.Dropout(0.25)(superres)

superres = layers.LayerNormalization()(superres)

# might not be needed!
superres = layers.Dense(N**2, activation='sigmoid')(superres)

#superres = layers.LayerNormalization()(superres)

final_image = layers.Reshape((N, N, 1))(superres)

# model definition
autoencoder = tf.keras.Model(input_img, final_image)

#opt = adam(lr=0.001, decay=1e-6)
#opt = keras.optimizers.SGD(learning_rate=0.01)
opt = SGD(learning_rate=0.1)

autoencoder.compile(optimizer=opt, loss=euclidean_distance_loss, metrics=['accuracy'])
autoencoder.summary()

#sys.exit()

#encoder = tf.keras.Model(input_img, encoded)

# load train and test images from stl10 dataset
(x_train, _), (x_test, _) = mnist.load_data()

# convert the stl10 dataset to grayscale
# x_train = rgb2gray(x_train)
# x_test = rgb2gray(x_test)

# normalize to float32 0 ... 1
x_train = x_train.astype('float32') / 255.
x_test = x_test.astype('float32') / 255.

# print(x_train.shape)
# print(x_test.shape)

# # resize the dataset to given dims
# x_train = resize(x_train, N)
# x_test = resize(x_test, N)

#x_train = x_train.reshape((len(x_train), np.prod(x_train.shape[1:])))
#x_test = x_test.reshape((len(x_test), np.prod(x_test.shape[1:])))
print(x_train.shape)
print(x_test.shape)

# train the AN
autoencoder.fit(x_train, x_train,
                epochs=1,
                batch_size=100,
                shuffle=True,
                validation_data=(x_test, x_test),
				callbacks=[TensorBoard(log_dir='/tmp/autoencoder')])

# use the trained model and display results
#imgs = autoencoder.predict(x_test)
#enc = encoder.predict(x_test)

sampler_image = x_test[0, :, :]
sampler_image_exp = np.expand_dims(sampler_image, axis=-1)
sampler_image_exp = np.expand_dims(sampler_image_exp, axis=0)

layer_name = 'dense'
intermediate_layer_model_1 = tf.keras.Model(inputs=autoencoder.input,
                                       outputs=autoencoder.get_layer(layer_name).output)
			
layer_name = 'multiply'
intermediate_layer_model_2 = tf.keras.Model(inputs=autoencoder.input,
                                       outputs=autoencoder.get_layer(layer_name).output)

layer_name = 'reshape_1'
intermediate_layer_model_3 = tf.keras.Model(inputs=autoencoder.input,
                                       outputs=autoencoder.get_layer(layer_name).output)	
	
intermediate_output_1 = intermediate_layer_model_1.predict(sampler_image_exp)
intermediate_output_2 = intermediate_layer_model_2.predict(sampler_image_exp)
#intermediate_output_3 = intermediate_layer_model_3.predict(sampler_image_exp)
			
#sys.exit()	
#intermediate_output = intermediate_layer_model(tf.reshape(x_test[1], [28, 28, 1]))

#print(intermediate_output.shape)

n = 1  # How many digits we will display
plt.figure(figsize=(20, 4))
for i in range(n):
    # # Display original
    ax = plt.subplot(2, n, i + 1)
    plt.imshow(x_test[0].reshape(N, N, 1))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # Display reconstruction
    ax = plt.subplot(2, n, i + 1 + n)
    #plt.imshow(intermediate_output[i].reshape(N, N, 1))
    plt.imshow(np.squeeze(intermediate_output_1[:, :, :, 0]))
    plt.summer()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.show()

n = 1  # How many digits we will display
plt.figure(figsize=(20, 4))
for i in range(n):
    # # Display original
    ax = plt.subplot(2, n, i + 1)
    plt.imshow(x_test[0].reshape(N, N, 1))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # Display reconstruction
    ax = plt.subplot(2, n, i + 1 + n)
    #plt.imshow(intermediate_output[i].reshape(N, N, 1))
    plt.imshow(np.squeeze(intermediate_output_2[:, :, :, 0]))
    plt.summer()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.show()

n = 10  # How many digits we will display
plt.figure(figsize=(20, 4))
for i in range(n):
    # # Display original
    ax = plt.subplot(2, n, i + 1)
    plt.imshow(x_test[i].reshape(N, N, 1))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # Display reconstruction
    ax = plt.subplot(2, n, i + 1 + n)
    #plt.imshow(intermediate_output[i].reshape(N, N, 1))
    plt.imshow(intermediate_layer_model_3.predict(x_test[i].reshape(N, N, 1)))
    plt.summer()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.show()