import numpy as np

from pyuoi.linear_model.poisson import Poisson

# poisson GLM model by hand

# design matrix
X = np.array([
    [0.35, 0.84, 0.95, 0.77, 0.88],
    [0.43, 0.76, 0.47, 0.09, 0.34],
    [0.41, 0.40, 0.08, 0.82, 0.49],
    [0.73, 0.93, 0.39, 0.77, 0.72],
    [0.69, 0.88, 0.32, 0.54, 0.26],
    [0.34, 0.10, 0.55, 0.20, 0.20],
    [0.20, 0.15, 0.23, 0.16, 0.74],
    [0.94, 0.08, 0.97, 0.03, 0.48],
    [0.61, 0.55, 0.72, 0.21, 0.27],
    [0.54, 0.21, 0.98, 0.26, 0.01]])

# true parameters
beta = np.array([3., 1., 0., -2., 0.])

# response variable
y = np.array([2, 6, 0, 4, 6, 3, 0, 16, 8, 7])


def test_soft_threshold():
    """Tests the soft threshold function against equivalent output from a
    MATLAB implementation."""

    true_threshold = np.array([
        [0, 0.34, 0.45, 0.27, 0.38],
        [0, 0.26, 0, 0, 0],
        [0, 0, 0, 0.32, 0],
        [0.23, 0.43, 0, 0.27, 0.22],
        [0.19, 0.38, 0, 0.04, 0],
        [0, 0, 0.05, 0, 0],
        [0, 0, 0.0, 0, 0.24],
        [0.44, 0, 0.47, 0, 0],
        [0.11, 0.05, 0.22, 0, 0],
        [0.04, 0, 0.48, 0, 0]])

    assert np.allclose(true_threshold,
                       Poisson.soft_threshold(X, 0.5))


def test_adjusted_response():
    """Tests the adjusted response function against equivalent output from a
    MATLAB implementation."""

    w, z = Poisson.adjusted_response(X, y, beta)

    w_true = np.array([
        1.419067548593257, 6.488296399286710, 0.990049833749168,
        4.854955811237434, 6.488296399286709, 2.054433210643888,
        1.537257523548281, 17.115765537145876, 7.099327065156633,
        3.706173712210199])

    z_true = np.array([
        0.759376179437427, 1.794741970890788, -1.01,
        1.403900392819534, 1.794741970890788, 1.180256767879915,
        -0.57, 2.774810655432013, 2.086867367368360,
        2.198740394692808])

    assert np.allclose(w_true, w)
    assert np.allclose(z_true, z)


def test_cd_sweep():
    """Test one pass through the coordinate sweep function."""

    poisson = Poisson(fit_intercept=False)

    w, z = Poisson.adjusted_response(X, y, beta)
    active_idx = np.argwhere(beta != 0).ravel()
    beta_new, intercept_new = poisson.cd_sweep(beta, X, w, z, active_idx)

    beta_new_true = np.array([
        2.922553187460584, 0.909849302128083, 0, -1.850644198436912, 0])

    assert np.allclose(beta_new_true, beta_new)
    assert intercept_new == 0


def test_fit():
    """Test the entire fitting procedure for the Poisson GLM."""

    # compare after 50 iterations
    poisson = Poisson(max_iter=50, fit_intercept=False)
    poisson.fit(X, y, init=0.5 * np.ones(beta.size))
    beta_new_true = np.array([
        -3.865910169523823, 6.243915946623266, -0.728804736275411,
        -0.463706073765083, -3.622620769371424])

    assert np.allclose(beta_new_true, poisson.coef_)
