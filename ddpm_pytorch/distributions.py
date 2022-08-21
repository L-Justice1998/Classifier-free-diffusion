from math import sqrt, log

import torch


def mu_x_t(x_t: torch.Tensor, t: torch.Tensor, model_noise: torch.Tensor, alphas_hat: torch.Tensor, betas: torch.Tensor, alphas: torch.Tensor) -> torch.Tensor:
    """

    :param x_t: the noised image
    :param t: the time step of $x_t$
    :param model_noise: the model estimated noise
    :param alphas_hat: sequence of $\hat{\alpha}$ used for variance scheduling
    :param betas: sequence of $\beta$ used for variance scheduling
    :param alphas: sequence of $\alpha$ used for variance scheduling
    :return: the mean of $q(x_t | x_0)$
    """
    x = 1 / sqrt(alphas[t].reshape(-1, 1, 1, 1)) * (x_t - betas[t].reshape(-1, 1, 1, 1) / sqrt(1 - alphas_hat[t].reshape(-1, 1, 1, 1)) * model_noise)
    # tg.guard(x, "B, C, W, H")
    return x


def sigma_x_t(v: torch.Tensor, t: torch.Tensor, betas_hat: torch.Tensor, betas: torch.Tensor) -> torch.Tensor:
    """
    Compute the varaince at time step t as defined in "Improving Denoising Diffusion probabilistic Models", eqn 15 page 4
    :param v: the neural network "logits" used to compute the variance [BS, C, W, H]
    :param t: the target time step
    :param betas_hat: sequence of $\hat{\beta}$ used for variance scheduling
    :param betas: sequence of $\beta$ used for variance scheduling
    :return: the estimated variance at time step t
    """
    x = torch.exp(v * log(betas[t].reshape(-1, 1, 1, 1)) + (1 - v) * log(betas_hat[t].reshape(-1, 1, 1, 1)))
    # tg.guard(x, "B, C, W, H")
    return x


def mu_hat_xt_x0(x_t: torch.Tensor, x_0: torch.Tensor, t: torch.Tensor, alphas_hat: torch.Tensor, alphas: torch.Tensor,
                 betas: torch.Tensor):
    """
    Compute $\hat{mu}(x_t, x_0)$ of $q(x_{t-1} | x_t, x_0)$ from "Improving Denoising Diffusion probabilistic Models", eqn 11 page 2
    :param x_t: The noised image at step t
    :param x_0: the original image
    :param t: the time step of $x_t$ [batch_size]
    :param alphas_hat: sequence of $\hat{\alpha}$ used for variance scheduling [T]
    :param alphas: sequence of $\alpha$ used for variance scheduling [T]
    :param betas: sequence of $\beta$ used for variance scheduling [T}
    :return: the mean of distribution $q(x_{t-1} | x_t, x_0)$
    """
    one_min_alpha_hat = (1 - alphas_hat[t].reshape(-1, 1, 1, 1))
    x = torch.sqrt(alphas_hat[t - 1].reshape(-1, 1, 1, 1)) * betas[t].reshape(-1, 1, 1, 1) / one_min_alpha_hat * x_0 + \
        torch.sqrt(alphas[t].reshape(-1, 1, 1, 1)) * (1 - alphas_hat[t - 1].reshape(-1, 1, 1, 1)) / one_min_alpha_hat * x_t
    # tg.guard(x, "B, C, W, H")
    return x


def sigma_hat_xt_x0(t: torch.Tensor, betas_hat: torch.Tensor) -> torch.Tensor:
    """
    Compute the variance of of $q(x_{t-1} | x_t, x_0)$ from "Improving Denoising Diffusion probabilistic Models", eqn 12 page 2
    :param t: the time step [batch_size]
    :param betas_hat: the array of beta hats [T]
    :return: the variance at time step t as scalar [batch_size, 1, 1, 1]
    """
    return betas_hat[t].reshape(-1, 1, 1, 1)