
from __future__ import print_function

import sys
import os
import shlex
import subprocess as sp
import pytest

from model import Model

class TestValgrind:

    def test_run(self, exp):
        """
        Run experiments
        """

        print('valgrind running with exp: {}'.format(exp.name))
        build = 'debug'
        compiler = 'gnu'
        # Build the model
        model = exp.get_model()
        m = Model(model)
        ret = m.build(build, compiler)
        assert(ret == 0)

        # Fake run to see what it would have done
        _, cmd_prefix, exe = exp.force_run(build, compiler, fake_it=True)

        # Construct a new command that includes valgrind
        cmd = cmd_prefix + ' valgrind ' + exe
        # Run the modified command
        saved_path = os.getcwd()
        os.chdir(exp.get_path())
        try:
            output = sp.check_output(shlex.split(cmd), stderr=sp.STDOUT)
        except sp.CalledProcessError as e:
            ret = e.returncode
        finally:
            with open('valgrind.out', 'r+') as f:
                print(e.output, file=f)
            os.chdir(saved_path)
        assert(ret == 0)

        # Do checks on valgrind output.