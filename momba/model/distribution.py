# -*- coding:utf-8 -*-
#
# Copyright (C) 2019, Maximilian Köhl <mkoehl@cs.uni-saarland.de>

from __future__ import annotations

import enum
import typing

from . import types


class Distribution(enum.Enum):
    DISCRETE_UNIFORM = 'DiscreteUniform', [types.INT, types.INT]
    BERNOULLI = 'Bernoulli', [types.REAL]
    BINOMIAL = 'Binomial', [types.REAL]
    NEGATIVE_BINOMIAL = 'NegativeBinomial', [types.REAL, types.REAL]
    POISSON = 'Poisson', [types.REAL]
    GEOMETRIC = 'Geometric', [types.REAL]
    HYPERGEOMETRIC = 'Hypergeometric', [types.INT, types.INT, types.INT]
    CONWAY_MAXWELL_POISSON = 'ConwayMaxwellPoisson', [types.REAL, types.REAL]
    ZIPF = 'ZipF', [types.REAL]
    UNIFORM = 'Uniform', [types.REAL, types.REAL]
    NORMAL = 'Normal', [types.REAL, types.REAL]
    LOG_NORMAL = 'LogNormal', [types.REAL, types.REAL]
    BETA = 'Beta', [types.REAL, types.REAL]
    CAUCHY = 'Cauchy', [types.REAL, types.REAL]
    CHI = 'Chi', [types.INT]
    CHI_SQUARED = 'ChiSquared', [types.INT]
    ERLANG = 'Erlang', [types.INT, types.REAL]
    EXPONENTIAL = 'Exponential', [types.REAL]
    FISHER_SNEDECOR = 'FisherSnedecor', [types.REAL, types.REAL]
    GAMMA = 'Gamma', [types.REAL, types.REAL]
    INVERSE_GAMMA = 'InverseGamma', [types.REAL, types.REAL]
    LAPLACE = 'Laplace', [types.REAL, types.REAL]
    PARETO = 'Pareto', [types.REAL, types.REAL]
    RAYLEIGH = 'Rayleigh', [types.REAL]
    STABLE = 'Stable', [types.REAL, types.REAL, types.REAL, types.REAL]
    STUDENT_T = 'StudentT', [types.REAL, types.REAL, types.REAL]
    WEIBULL = 'Weibull', [types.REAL, types.REAL]
    TRIANGULAR = 'Triangular', [types.REAL, types.REAL, types.REAL]

    jani_name: str
    parameter_types: typing.Sequence[types.Type]

    def __init__(self, name: str, parameter_types: typing.Sequence[types.Type]) -> None:
        self.jani_name = name
        self.parameter_types = parameter_types
