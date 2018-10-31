#! /usr/bin/env python3

import math
import unittest

import torch
from botorch import fit_model
from botorch.models import GPRegressionModel
from botorch.optim.fit import fit_torch
from gpytorch.likelihoods import GaussianLikelihood
from gpytorch.mlls.exact_marginal_log_likelihood import ExactMarginalLogLikelihood


NOISE = [0.127, -0.113, -0.345, -0.034, -0.069, -0.272, 0.013, 0.056, 0.087, -0.081]


class TestFitModel(unittest.TestCase):
    def setUp(self):
        self.train_x = torch.linspace(0, 1, 10)
        self.train_y = torch.sin(self.train_x * (2 * math.pi)) + torch.tensor(NOISE)

    def test_fit_model(self, cuda=False):
        train_x = self.train_x.cuda() if cuda else self.train_x
        train_y = self.train_y.cuda() if cuda else self.train_y
        likelihood = GaussianLikelihood()
        model = GPRegressionModel(train_x.detach(), train_y.detach(), likelihood)
        mll = ExactMarginalLogLikelihood(likelihood, model)

        mll = fit_model(mll, options={"maxiter": 1})

        # Make sure all of the parameters changed
        self.assertGreater(model.likelihood.log_noise.abs(), 1e-3)
        self.assertGreater(model.mean_module.constant.abs(), 1e-3)
        self.assertGreater(model.covar_module.base_kernel.log_lengthscale.abs(), 1e-3)
        self.assertGreater(model.covar_module.log_outputscale.abs(), 1e-3)

        # Test with torch fit
        mll = fit_model(mll, optimizer=fit_torch, maxiter=1)

    def test_fit_model_cuda(self):
        if torch.cuda.is_available():
            self.test_fit_model(cuda=True)


if __name__ == "__main__":
    unittest.main()