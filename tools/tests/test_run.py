
from __future__ import print_function

import sys
import os
import pytest

from model import Model

class TestRun:

    def test_run(self, exp, build, compiler):
        """
        Run experiments 
        """
        model = exp.get_model()
        m = Model(model)
        ret = m.build(build, compiler)
        assert(ret == 0)

        ret = exp.run(build, compiler)
        assert(ret == 0)
