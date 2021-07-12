import tensorflow as tf

import glob
import imageio
import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
from tensorflow.keras import layers
import time

from IPython import display

import tensorflow.keras.backend as K
#from tf.keras.utils import plot_model
#from tf.keras import Model

import sys

mask_modulation_num = 500
N = 28
	
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
	
# https://www.tensorflow.org/tutorials/generative/dcgan
def make_generator_model():
	model = tf.keras.Sequential()
	
	model.add(layers.Dense(7*7*1200, use_bias=False, input_shape=(100,)))
	model.add(layers.BatchNormalization())
	model.add(layers.LeakyReLU())
	
	model.add(layers.Reshape((7, 7, 1200)))
	assert model.output_shape == (None, 7, 7, 1200)  # Note: None is the batch size

	model.add(layers.Conv2DTranspose(900, (5, 5), strides=(1, 1), padding='same', use_bias=False))
	assert model.output_shape == (None, 7, 7, 900)
	model.add(layers.BatchNormalization())
	model.add(layers.LeakyReLU())

	model.add(layers.Conv2DTranspose(600, (5, 5), strides=(2, 2), padding='same', use_bias=False))
	assert model.output_shape == (None, 14, 14, 600)
	model.add(layers.BatchNormalization())
	model.add(layers.LeakyReLU())

	model.add(layers.Conv2DTranspose(300, (5, 5), strides=(2, 2), padding='same', use_bias=False, activation='tanh', activity_regularizer=binary_reg))
	assert model.output_shape == (None, 28, 28, 300)

	return model

def make_reconstructor_model():
	model = tf.keras.Sequential()
	
	model.add(layers.Dense(N**2, activation='relu', input_shape=(300, )))
	
	# model.add(layers.Conv2D(int(N/2), (9, 9), 1, activation='relu'))
	# model.add(layers.MaxPooling2D((2, 2)))
	# model.add(layers.Dropout(0.25))
	# model.add(layers.LayerNormalization())
	
	# model.add(layers.Conv2D(int(N/4), (1, 1), int(N/2), activation='relu'))
	# model.add(layers.MaxPooling2D((2, 2)))
	# model.add(layers.Dropout(0.25))
	# model.add(layers.LayerNormalization())
	
	# model.add(layers.Conv2D(int(N/4), (1, 1), int(N/2), activation='relu'))
	# model.add(layers.MaxPooling2D((2, 2)))
	# model.add(layers.Dropout(0.25))
	# model.add(layers.LayerNormalization())

	# model.add(layers.Conv2D(1, (5, 5), int(N/4), activation='relu'))
	# model.add(layers.MaxPooling2D((2, 2)))
	# model.add(layers.Dropout(0.25))
	# model.add(layers.LayerNormalization())
	
	model.add(layers.Dense(N**2, activation='sigmoid'))
	
	model.add(layers.Reshape((N, N, 1)))
	assert model.output_shape == (None, N, N, 1)
	
	return model
	
generator = make_generator_model()
reconstructor = make_reconstructor_model()

generator.summary()
reconstructor.summary()

#sys.exit()

generator_optimizer = tf.keras.optimizers.Adam(1e-4)
reconstructor_optimizer = tf.keras.optimizers.Adam(1e-4)

epochs = 2
noise_dim = 100
num_examples_to_generate = 16

seed = tf.random.normal([num_examples_to_generate, noise_dim])

checkpoint_dir = './training_checkpoints'
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
checkpoint = tf.train.Checkpoint(generator_optimizer=generator_optimizer,
                                 reconstructor_optimizer=reconstructor_optimizer,
                                 generator=generator,
                                 reconstructor=reconstructor)

@tf.function
def train_step(images):
	noise = tf.random.normal([BATCH_SIZE, noise_dim])

	with tf.GradientTape() as gen_tape, tf.GradientTape() as rec_tape:
		masking_patterns = generator(noise, training=True)

		temp_vector = tf.zeros([0, 300])
		measurement_vector = tf.zeros([20, 300])
		
		for image in images:
			masked_image = image * masking_patterns
			intensity = tf.reduce_sum(masked_image, [1, 2])
			measurement_vector = tf.concat([temp_vector, intensity], axis=0)

		reconstructed_images = reconstructor(measurement_vector, training=True)

		gen_loss = euclidean_distance_loss(images, reconstructed_images)
		rec_loss = euclidean_distance_loss(images, reconstructed_images)

	gradients_of_generator = gen_tape.gradient(gen_loss, generator.trainable_variables)
	gradients_of_reconstructor = rec_tape.gradient(rec_loss, reconstructor.trainable_variables)

	generator_optimizer.apply_gradients(zip(gradients_of_generator, generator.trainable_variables))
	reconstructor_optimizer.apply_gradients(zip(gradients_of_reconstructor, reconstructor.trainable_variables))

def train(dataset, epochs):
	for epoch in range(epochs):
		start = time.time()

		i = 1

		for image_batch in dataset:
			train_step(image_batch)
			print("Batch " + str(i))
			i+=1

		# Produce images for the GIF as you go
		display.clear_output(wait=True)
		generate_and_save_images(	generator,
									epoch + 1,
									seed,
									"generator")
									
		mask_and_save_images(	generator,
								reconstructor,
								epoch + 1,
								seed,
								"reconstructor")
								
		# Save the model every 15 epochs
		if (epoch + 1) % 15 == 0:
			checkpoint.save(file_prefix = checkpoint_prefix)

		print ('Time for epoch {} is {} sec'.format(epoch + 1, time.time()-start))

	# Generate after the final epoch
	display.clear_output(wait=True)
	generate_and_save_images(	generator,
								epoch + 1,
								seed,
								"generator")
									
	mask_and_save_images(	generator,
							reconstructor,
							epoch + 1,
							seed,
							"reconstructor")

def mask_and_save_images(model_gen, model_rec, epoch, test_input, name="null"):
	# Notice `training` is set to False.
	# This is so all layers run in inference mode (batchnorm).
	masks = model_gen(test_input, training=False)

	temp_vector = tf.zeros([0, 300])
	measurement_vector = tf.zeros([20, 300])
		
	for image in images:
		masked_image = image * masking_patterns
		intensity = tf.reduce_sum(masked_image, [1, 2])
		measurement_vector = tf.concat([temp_vector, intensity], axis=0)

	predictions = model_rec(measurement_vector, training=False)

	fig = plt.figure(figsize=(4, 4))

	for i in range(predictions.shape[0]):
		plt.subplot(4, 4, i+1)
		plt.imshow(predictions[i, :, :, 0] * 127.5 + 127.5, cmap='gray')
		plt.axis('off')

	plt.savefig(str(name) + '_at_epoch_{:04d}.png'.format(epoch))
	plt.show()
	
	return predictions

def generate_and_save_images(model, epoch, test_input, name="null"):
	# Notice `training` is set to False.
	# This is so all layers run in inference mode (batchnorm).
	predictions = model(test_input, training=False)

	fig = plt.figure(figsize=(4, 4))

	for i in range(predictions.shape[0]):
		plt.subplot(4, 4, i+1)
		plt.imshow(predictions[i, :, :, 0] * 127.5 + 127.5, cmap='gray')
		plt.axis('off')

	plt.savefig(str(name) + '_at_epoch_{:04d}.png'.format(epoch))
	plt.show()
	
	return predictions

(train_images, _), (_, _) = tf.keras.datasets.mnist.load_data()
train_images = train_images.reshape(train_images.shape[0], 28, 28, 1).astype('float32')
train_images = (train_images - 127.5) / 127.5  # Normalize the images to [-1, 1]

BUFFER_SIZE = 60000
BATCH_SIZE = 20

# Batch and shuffle the data
train_dataset = tf.data.Dataset.from_tensor_slices(train_images).shuffle(BUFFER_SIZE).batch(BATCH_SIZE)
print(train_dataset)

# Generate after the final epoch
display.clear_output(wait=True)
preds = generate_and_save_images(	generator,
									epochs,
									seed,
									"generator")
							
mask_and_save_images(	generator,
						reconstructor,
						epochs,
						seed,
						"reconstructor")

train(train_dataset, epochs)

anim_file = 'dcgan_generator.gif'
anim_file = 'dcgan_reconstructor.gif'

with imageio.get_writer(anim_file, mode='I') as writer:
  filenames = glob.glob('generator*.png')
  filenames = sorted(filenames)
  for filename in filenames:
    image = imageio.imread(filename)
    writer.append_data(image)
  image = imageio.imread(filename)
  writer.append_data(image)

import tensorflow_docs.vis.embed as embed
embed.embed_file(anim_file)

with imageio.get_writer(anim_file, mode='I') as writer:
  filenames = glob.glob('reconstructor*.png')
  filenames = sorted(filenames)
  for filename in filenames:
    image = imageio.imread(filename)
    writer.append_data(image)
  image = imageio.imread(filename)
  writer.append_data(image)

import tensorflow_docs.vis.embed as embed
embed.embed_file(anim_file)

sys.exit()