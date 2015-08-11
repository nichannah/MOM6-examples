
from __future__ import print_function

import sys
import os
import pytest
import shlex
import subprocess as sp

from model import Model

class TestSetup:

    def test_download_ocean_only(self):
        """
        Test to download the ocean only code.

        Of course MOM6-examples must have been downloaded to bootstrap the
        process.
        """

        root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', '../')
        os.chdir(root)

        assert(os.path.exists('.git'))
        sp.check_call(shlex.split('git submodule init'))
        sp.check_call(shlex.split('git submodule update'))


    def test_download_ocean_ice(self):
        """
        Test to download the ocean, ice and coupler code.
        """

        root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', '../')
        os.chdir(root)

    def test_download_input(self):

        root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', '../')
        os.chdir(root)
