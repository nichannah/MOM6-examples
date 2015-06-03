
from __future__ import print_function

import sys
import os
import pytest

from model import Model

class TestBuild:

    def test_build(self, model, build, compiler):
        """
        Test whether a model builds with various build types
        (debug, repro, release) on various compilers
        """
        m = Model(model)
        ret = m.build(build, compiler)
        assert(ret == 0)
