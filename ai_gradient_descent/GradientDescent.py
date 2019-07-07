import tensorflow as tf
import matplotlib.pyplot as plt


class Model(object):
    def __init__(self):
        # Initialize variable to (5.0, 0.0)
        # In practice, these should be initialized to random values.
        self.theta = tf.Variable([[-1.0], [-4.0]])

    def __call__(self, x):
        return tf.matmul(x, self.theta)


def loss(predicted_y, desired_y):
    ret = tf.reduce_mean(tf.square(predicted_y - desired_y))
    return ret


def train(model, inputs, outputs, learning_rate):
    with tf.GradientTape() as t:
        current_loss = loss(model(inputs), outputs)
        dTheta = t.gradient(current_loss, model.theta)
        model.theta.assign_sub(learning_rate * dTheta)


if __name__ == "__main__":

    model = Model()

    TRUE_THETA = [[5.0], [1.0]]
    NUM_EXAMPLES = 1000

    inputs, outputs, outputs_graph, inputs_first_degree = [], [], [], []

    for i in range(NUM_EXAMPLES):
        input = tf.random.normal(shape=[1, 2])
        noise = tf.random.normal(shape=[1])
        outputs.append(tf.matmul(input, TRUE_THETA) + noise)
        inputs.append(input)
        inputs_first_degree.append(input.numpy()[0][0])
        outputs_graph.append((tf.matmul(input, TRUE_THETA) + noise).numpy()[0][0])
    #endfor

    plt.scatter(inputs_first_degree, outputs_graph, c='b')
    plt.scatter(inputs_first_degree, model(inputs), c='r')
    plt.show()

    print('Current loss: '),
    print(loss(model(inputs), outputs).numpy())

    thetas = []
    losses = []
    epochs = range(50)
    for epoch in epochs:
        thetas.append(model.theta.numpy())
        current_loss = loss(model(inputs), outputs)
        losses.append(current_loss.numpy())
        train(model, inputs, outputs, learning_rate=0.05)
        #print('Epoch %2d: Theta=%s , loss=%2.5f \n' %(epoch, str(thetas[-1]), current_loss))

    # Let's plot it all
    #     plt.plot(epochs, thetas, 'r')
    # plt.plot([TRUE_THETA] * len(epochs), 'r--')

    plt.scatter(inputs_first_degree, outputs_graph, c='b')
    plt.scatter(inputs_first_degree, model(inputs), c='r')
    plt.legend(['true theta', 'trained theta'])
    plt.show()

    plt.scatter(epochs, losses, c='b')
    plt.legend(['loss function of iteration number'])
    plt.show()
