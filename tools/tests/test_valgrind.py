
from __future__ import print_function

import sys
import os
import shlex
import subprocess as sp
import pytest
import re

from model import Model

VALGRIND_MPI_WRAPPER_PATH = '/home/599/nah599/more_home/usr/local/lib/valgrind/'
VALGRIND_EXE_PATH = '/home/599/nah599/more_home/usr/local/bin/'

class TestValgrind:

    def test_run(self, exp):
        """
        Run experiments
        """

        print('valgrind running with exp: {}'.format(exp.name))
        build = 'debug'
        compiler = 'intel'
        # Build the model
        model = exp.get_model()
        m = Model(model)
        ret = m.build(build, compiler)
        assert(ret == 0)

        # Fake run to see what it would have done
        _, cmd_prefix, exe = exp.force_run(build, compiler, fake_it=True)

        # Construct a new command that includes valgrind
        my_dir = os.path.dirname(os.path.abspath(__file__))
        cmd = cmd_prefix + ' -x LD_PRELOAD={}/libmpiwrap-amd64-linux.so {}/valgrind --main-stacksize=2000000000 --max-stackframe=2000000000 --error-limit=no --track-origins=yes -v --gen-suppressions=all --suppressions={}/valgrind_suppressions.txt '.format(VALGRIND_MPI_WRAPPER_PATH, VALGRIND_EXE_PATH, my_dir) + exe

        # Run the modified command
        saved_path = os.getcwd()
        os.chdir(exp.get_path())
        output = ''
        try:
            output = sp.check_output(shlex.split(cmd), stderr=sp.STDOUT)
        except sp.CalledProcessError as e:
            ret = e.returncode
            output = e.output
        finally:
            with open('valgrind.out', 'w') as f:
                print(output, file=f)
            print(output)
            os.chdir(saved_path)
        assert(ret == 0)

        # Do checks on valgrind output.
        errs = re.findall('ERROR SUMMARY: (\d+) errors from \d+ contexts', output)
        assert(len(errs) != 0)
        errs = map(int, errs)
        assert(sum(errs) == 0)
