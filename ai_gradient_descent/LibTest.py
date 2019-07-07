import tensorflow as tf


class Model(object):
    def __init__(self):
        # Initialize variable to (5.0, 0.0)
        # In practice, these should be initialized to random values.
        self.theta = tf.Variable([[-1.0], [-4.0]])

    def __call__(self, x):
        return tf.matmul(x, self.theta)


def loss(prediction, epoch_number):
    return tf.reduce_mean(tf.square((50 + prediction - epoch_number * 1.342)))

# def loss(epoch_number):
#     return tf.reduce_mean(tf.square((50 - epoch_number * 1.342)))


def train(model, inputs, learning_rate, epoch):
    with tf.GradientTape() as t:
        loss_nr = loss(model(inputs), epoch) #WILL WORK
        # loss_nr = loss(epoch) #WILL NOT WORK
        dTheta = t.gradient(loss_nr, model.theta)
        model.theta.assign_sub(learning_rate * dTheta)
        print model.theta


if __name__ == "__main__":
    epochs = range(5)
    thetas, losses = [], []

    model = Model()
    inputs = []
    for i in range(100):
        inputs.append(tf.random.normal(shape=[1, 2]))

    for epoch in epochs:
        thetas.append(model.theta.numpy())
        train(model, inputs, learning_rate=0.05, epoch=epoch)
        #print('Epoch %2d: Theta=%s , loss=%2.5f \n' %(epoch, str(thetas[-1]), current_loss))