import tensorflow as tf
from inits import *

flags = tf.flags
FLAGS = flags.FLAGS

# global unique layer ID dictionary for layer name assignment
_LAYER_UIDS = {}


def dot(x, y, sparse=False):
    """Wrapper for tf.matmul (sparse vs dense)."""
    if sparse:
        res = tf.sparse.sparse_dense_matmul(x, y)
    else:
        res = tf.matmul(x, y)
    return res


class GraphConvolution(object):
    """Graph convolution layer."""
    # 参数：输入维度、输出维度、邻接矩阵（元祖表示）、输入X
    def __init__(self, input_dim, output_dim, adj, inputs, act=tf.nn.sigmoid, bias=False):
        self.inputs = inputs
        self.act = act
        self.support = adj
        self.bias = bias
        self.output_dim = output_dim
        # print(input_dim, output_dim) -0.35, 0.35 tf.random_uniform([input_dim, output_dim], -0.35, 0.35),
        with tf.variable_scope('_vars'):
            self.weights = tf.Variable(tf.random.truncated_normal([input_dim, output_dim], -0.35, 0.35),
                                       name='weights_', dtype=tf.float32)
            # self.weights = tf.get_variable(name='weights_{}'.format(output_dim), dtype=tf.float32, shape=(input_dim, output_dim),
            #                                initializer=tf.contrib.layers.xavier_initializer())
            if self.bias:
                self.bias = tf.Variable(tf.random.truncated_normal([output_dim]), name='bias', dtype=tf.float32)

    # 计算AXW
    def out(self):
        x = self.inputs
        output = tf.matmul(self.support, x)

        output = tf.matmul(output, self.weights)
        
        # bias
        if self.bias:
            output += self.bias
        return self.act(output)

# def sparse_dropout(x, keep_prob, noise_shape):
#     """Dropout for sparse tensors."""
#     random_tensor = keep_prob
#     random_tensor += tf.random_uniform(noise_shape)
#     dropout_mask = tf.cast(tf.floor(random_tensor), dtype=tf.bool)
#     pre_out = tf.sparse_retain(x, dropout_mask)
#     return pre_out * (1./keep_prob)
#
# def get_layer_uid(layer_name=''):
#     """Helper function, assigns unique layer IDs."""
#     if layer_name not in _LAYER_UIDS:
#         _LAYER_UIDS[layer_name] = 1
#         return 1
#     else:
#         _LAYER_UIDS[layer_name] += 1
#         return _LAYER_UIDS[layer_name]
#
# class Layer(object):
#     """Base layer class. Defines basic API for all layer objects.
#     Implementation inspired by keras (http://keras.io).
#
#     # Properties
#         name: String, defines the variable scope of the layer.
#         logging: Boolean, switches Tensorflow histogram logging on/off
#
#     # Methods
#         _call(inputs): Defines computation graph of layer
#             (i.e. takes input, returns output)
#         __call__(inputs): Wrapper for _call()
#         _log_vars(): Log all variables
#     """
#
#     def __init__(self, **kwargs):
#         allowed_kwargs = {'name', 'logging'}
#         for kwarg in kwargs.keys():
#             assert kwarg in allowed_kwargs, 'Invalid keyword argument: ' + kwarg
#         name = kwargs.get('name')
#         if not name:
#             layer = self.__class__.__name__.lower()
#             name = layer + '_' + str(get_layer_uid(layer))
#         self.name = name
#         self.vars = {}
#         logging = kwargs.get('logging', False)
#         self.logging = logging
#         self.sparse_inputs = False
#
#
# class GraphConvolution(Layer):
#     """Graph convolution layer."""
#     def __init__(self, input_dim, output_dim, placeholders, dropout=0.,
#                  sparse_inputs=False, act=tf.nn.relu, bias=False,
#                  featureless=False, **kwargs):
#         super(GraphConvolution, self).__init__(**kwargs)
#
#         if dropout:
#             self.dropout = placeholders['dropout']
#         else:
#             self.dropout = 0.
#
#         self.act = act
#         self.support = placeholders['support']
#         self.sparse_inputs = sparse_inputs
#         self.featureless = featureless
#         self.bias = bias
#
#         # helper variable for sparse dropout
#         self.num_features_nonzero = placeholders['num_features_nonzero']
#
#         with tf.variable_scope(self.name + '_vars'):
#             for i in range(len(self.support)):
#                 self.vars['weights_' + str(i)] = glorot([input_dim, output_dim],
#                                                         name='weights_' + str(i))
#             if self.bias:
#                 self.vars['bias'] = zeros([output_dim], name='bias')
#
#         if self.logging:
#             self._log_vars()
#
#     def _call(self, inputs):
#         x = inputs
#
#         # dropout
#         if self.sparse_inputs:
#             x = sparse_dropout(x, 1-self.dropout, self.num_features_nonzero)
#         else:
#             x = tf.nn.dropout(x, 1-self.dropout)
#
#         # convolve
#         supports = list()
#         for i in range(len(self.support)):
#             if not self.featureless:
#                 pre_sup = dot(x, self.vars['weights_' + str(i)],
#                               sparse=self.sparse_inputs)
#             else:
#                 pre_sup = self.vars['weights_' + str(i)]
#             support = dot(self.support[i], pre_sup, sparse=True)
#             supports.append(support)
#         output = tf.add_n(supports)
#
#         # bias
#         if self.bias:
#             output += self.vars['bias']
#
#         return self.act(output)
