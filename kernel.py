from kernel_pca import KernelPCA
import numpy as np
import re

DEFAULT_RANDOM_DISTRIBUTION_SIZE = 10
DEFAULT_POLYNOMIAL_DEGREE = 2
DEFAULT_GAMMA_RANGE = [-1, 1]
DEFAULT_R_RANGE = [1, 3]
DEFAULT_EXPONENT = 5
DEFAULT_SIGMOID_COEFFICIENT_RANGE = [-1, 0]
DEFAULT_SIGMOID_MANIPULATION = lambda x: x
DEFAULT_RBF_MANIPULATION = lambda x: x
DEFAULT_POLYNOMIAL_MANIPULATION = lambda x: x

KERNELS = ['spd', 'poly', 'sigmoid', 'rbf']


class Kernel:
    def __init__(self, kernel_config, components_num, avg_euclidean_distances, max_euclidean_distances,
                 normalization_method, random, divide_after_combination=False):
        self.kernel_params = {}
        self.avg_euclidean_distances = avg_euclidean_distances
        self.max_euclidean_distances = max_euclidean_distances
        self.kernel_combine = None
        self.alpha = None
        self.normalization_method = normalization_method
        self.n_components = components_num
        if kernel_config['name'] == 'mix':
            self.kernel_name = random.choice(KERNELS)
        else:
            self.kernel_name = kernel_config['name']
        if '+' in self.kernel_name:
            self.kernel_combine = '+'
            self.alpha = random.uniform(0, 1)
        elif '*' in self.kernel_name:
            self.kernel_combine = '*'
        for kernel_name in re.split('[*+]', self.kernel_name):
            self._generate_kernel(kernel_config, kernel_name, random)
        self.kernel = KernelPCA(n_components=self.n_components, kernel_params=self.kernel_params,
                                kernel_combine=self.kernel_combine, alpha=self.alpha,
                                normalization_method=self.normalization_method,
                                divide_after_combination=divide_after_combination)

    def _generate_kernel(self, kernel_config, kernel_name, random):
        kernel_inner_params = {
            "gamma": None,
            "coef0": 1,
            "degree": 3
        }
        if self.alpha:
            kernel_inner_params['alpha'] = self.alpha
        if kernel_name in ('linear', 'spd'):
            pass
        elif kernel_name == 'poly':
            gamma_range = kernel_config['poly_gamma'] if 'poly_gamma' in kernel_config else DEFAULT_GAMMA_RANGE
            gamma = random.uniform(gamma_range[0], gamma_range[1])
            degree = kernel_config['poly_degree'] if 'poly_degree' in kernel_config else DEFAULT_POLYNOMIAL_DEGREE
            kernel_inner_params['gamma'] = gamma
            kernel_inner_params['degree'] = degree
            kernel_inner_params['manipulation'] = DEFAULT_POLYNOMIAL_MANIPULATION
        elif kernel_name == 'sigmoid':
            distribution_size = kernel_config['distribution_size'] if 'distribution_size' in kernel_config else \
                DEFAULT_RANDOM_DISTRIBUTION_SIZE
            avg_random_distribution = np.mean([random.uniform(0, 1) for _ in range(distribution_size)])
            exp = kernel_config['sig_exp'] if 'sig_exp' in kernel_config else DEFAULT_EXPONENT
            gamma = kernel_config['sig_gamma'] if 'sig_gamma' in kernel_config else 1 / (avg_random_distribution ** exp)
            sig_coef = kernel_config['sig_coef'] if 'sig_coef' in kernel_config else DEFAULT_SIGMOID_COEFFICIENT_RANGE
            coef0 = random.uniform(sig_coef[0], sig_coef[1])
            kernel_inner_params['gamma'] = gamma
            kernel_inner_params['coef0'] = coef0
            kernel_inner_params['manipulation'] = DEFAULT_SIGMOID_MANIPULATION
        elif kernel_name == 'rbf':
            rbf_r = kernel_config['rbf_r'] if 'rbf_r' in kernel_config else DEFAULT_R_RANGE
            r = random.uniform(rbf_r[0], rbf_r[1])
            gamma = kernel_config['rbf_gamma'] if 'rbf_gamma' in kernel_config \
                else 1 / (self.avg_euclidean_distances ** r)
            kernel_inner_params['gamma'] = gamma
            kernel_inner_params['manipulation'] = DEFAULT_RBF_MANIPULATION
        elif kernel_name == 'laplacian':
            distribution_size = kernel_config['distribution_size'] if 'distribution_size' in kernel_config else \
                DEFAULT_RANDOM_DISTRIBUTION_SIZE
            avg_random_distribution = np.mean([random.uniform(0, 1) for _ in range(distribution_size)])
            exp = kernel_config['lap_exp'] if 'lap_exp' in kernel_config else DEFAULT_EXPONENT
            gamma = kernel_config['lap_gamma'] if 'lap_gamma' in kernel_config else 1 / (avg_random_distribution ** exp)
            kernel_inner_params['gamma'] = gamma
        else:
            raise NotImplementedError('Unsupported kernel')
        self.kernel_params[kernel_name] = kernel_inner_params

    def calculate_kernel(self, x, is_test=False):
        if is_test:
            return self.kernel.transform(x)
        else:
            return self.kernel.fit_transform(x)

    def to_string(self):
        return str(self.kernel_params)
