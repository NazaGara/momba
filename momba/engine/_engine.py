# -*- coding:utf-8 -*-
#
# Copyright (C) 2020, Maximilian Köhl <koehl@cs.uni-saarland.de>

try:
    import momba_engine as engine
except ImportError:
    raise ImportError(
        "Missing optional dependency `momba_engine`.\n"
        "Using Momba's engine requires installing `momba_engine`."
    )


__all__ = ["engine"]
