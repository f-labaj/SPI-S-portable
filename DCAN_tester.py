import tensorflow as tf

(x_train, _), (x_test, _) = tf.keras.datasets.mnist.load_data()

x_test = x_test.reshape(x_test.shape[0], 28, 28, 1).astype('float32') / 255

model = tf.keras.models.load_model("GANDCAN_model")
pred = full.predict(x_test[1])