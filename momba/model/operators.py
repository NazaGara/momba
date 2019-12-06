# -*- coding:utf-8 -*-
#
# Copyright (C) 2019, Maximilian Köhl <mkoehl@cs.uni-saarland.de>

from __future__ import annotations

import enum


class BinaryOperator:
    pass


class BooleanOperator(BinaryOperator, enum.Enum):
    AND = '∧'
    OR = '∨'
    XOR = '⊕'
    IMPLY = '⇒'
    EQUIV = '⇔'


class ArithmeticOperator(BinaryOperator, enum.Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    MOD = '%'


class EqualityOperator(BinaryOperator, enum.Enum):
    EQ = '='
    NEQ = '≠'


class ComparisonOperator(BinaryOperator, enum.Enum):
    LT = '<'
    LE = '≤'
    GE = '≥'
    GT = '>'
