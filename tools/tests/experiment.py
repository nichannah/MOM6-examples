
from __future__ import print_function

import sys
import os
import re
import shlex
import string
import subprocess as sp
import run_config as rc
from model import Model

# Only support Python version >= 2.7
assert(not(sys.version_info[0] == 2) or sys.version_info[1] >= 7)

_file_dir = os.path.dirname(os.path.abspath(__file__))
_mom_examples_path = os.path.normpath(os.path.join(_file_dir, '../../'))

class Diagnostic:

    def __init__(self, model, name, path):
        self.model = model
        self.name = name
        self.full_name = '{}_{}'.format(model, name)
        self.output = os.path.join(path, '00010101.{}.nc'.format(self.full_name))

    def __eq__(self, other):
        return ((self.model, self.name, self.output) ==
                (other.model, other.name, other.output))

    def __hash__(self):
        return hash(self.model + self.name + self.output)


# Unfinished diagnostics are those which have been registered but have not been
# implemented, so no post_data called. This list should to be updated as the
# diags are completed.
_unfinished_diags = [('ocean_model', 'uml_restrat'),
                     ('ocean_model', 'vml_restrat'),
                     ('ocean_model', 'created_H'),
                     ('ocean_model', 'seaice_melt'),
                     ('ocean_model', 'fsitherm'),
                     ('ocean_model', 'total_seaice_melt'),
                     ('ocean_model', 'heat_restore'),
                     ('ocean_model', 'total_heat_restore'),
                     ('ocean_model_z_new', 'TKE_to_Kd'),
                     ('ice_model', 'Cor_ui'),
                     ('ice_model', 'Cor_vi'),
                     ('ice_model', 'OBI'),
                     ('ice_model', 'RDG_OPEN'),
                     ('ice_model', 'RDG_RATE'),
                     ('ice_model', 'RDG_VOSH'),
                     ('ice_model', 'STRAIN_ANGLE'),
                     ('ice_model', 'SW_DIF'),
                     ('ice_model', 'SW_DIR'),
                     ('ice_model', 'TA')]

def exp_id_from_path(path):
    """
    Return an experiment id string of the form <model>/<exp>/<variation> from a
    full path.
    """
    path = os.path.normpath(path)
    path = path.replace(_mom_examples_path, '')
    # Remove possible '/' from front and back.
    return string.strip(path, '/')

class Experiment:

    def __init__(self, id, compiler='gnu', build='DEBUG', memory_type='dynamic'):
        """
        Python representation of an experiment/test case.

        The id is a string of the form <model>/<exp>/<variation>.
        """

        self.compiler = compiler
        self.build = build
        self.memory_type = memory_type
        id = id.split('/')
        self.model_name = id[0]
        self.name = id[1]
        if len(id) == 3:
            self.variation = id[2]
        else:
            self.variation = None

        self.model = Model(self.model_name, _mom_examples_path)

        self.path = os.path.join(_mom_examples_path, self.model_name,
                                 self.name)
        if self.variation is not None:
            self.path = os.path.join(self.path, self.variation)

        self.exec_path = None

        # Lists of available and unfinished diagnostics.
        self.available_diags = self._parse_available_diags()
        self.unfinished_diags = [Diagnostic(m, d, self.path) \
                                 for m, d in _unfinished_diags]
        # Available diags is not what you think! Need to remove the unfinished
        # diags.
        self.available_diags = list(set(self.available_diags) - \
                                    set(self.unfinished_diags))
        # It helps with testing and human readability if this is sorted.
        self.available_diags.sort(key=lambda d: d.full_name)

        # Whether this experiment has been run. Want to try to avoid
        # repeating this if possible.
        self.has_run = False
        # Another thing to avoid repeating.
        self.has_dumped_diags = False

    def _parse_available_diags(self):
        """
        Create a list of available diags for the experiment by parsing
        available_diags.000001 and SIS.available_diags.
        """
        mom_av_file = os.path.join(self.path, 'available_diags.000000')
        sis_av_file = os.path.join(self.path, 'SIS.available_diags')

        diags = []
        for fname in [mom_av_file, sis_av_file]:
            # If available diags file doesn't exist then just skip for now.
            if not os.path.exists(fname):
                continue
            with open(fname) as f:
                # Search or strings like: "ocean_model", "N2_u"  [Unused].
                # Pull out the model name and variable name.
                matches = re.findall('^\"(\w+)\", \"(\w+)\".*$',
                                     f.read(), re.MULTILINE)
                diags.extend([Diagnostic(m, d, self.path) for m, d in matches])
        return diags

    def build_model(self):
        """
        Build the configuration for this experiment.
        """

        if not self.exec_path:
            ret, exe = self.model.build(self.compiler, self.build,
                                     self.memory_type)
            assert(ret == 0)
            self.exec_path = exe

    def run(self):
        """
        Run the experiment if it hasn't already.
        """

        if not self.has_run:
            return self.force_run()

    def force_run(self):
        """
        Run the experiment.
        """

        self.build_model()
        assert(os.path.exists(self.exec_path))

        ret = 0
        saved_path = os.getcwd()

        os.chdir(self.path)
        try:
            exe = rc.get_exec_prefix(self.model, self.name, self.variation) + \
                  ' ' + self.exec_path
            print('Executing ' + exe)
            output = sp.check_output(shlex.split(exe), stderr=sp.STDOUT)
            self.has_run = True
        except sp.CalledProcessError as e:
            ret = e.returncode
            print(e.output, file=sys.stderr)
        finally:
            os.chdir(saved_path)

        return ret

    def get_available_diags(self):
        """
        Return a list of the available diagnostics for this experiment.
        """
        return self.available_diags

    def get_unfinished_diags(self):
        """
        Return a list of the unfinished diagnostics for this experiment.
        """
        return self.unfinished_diags


def discover_experiments():
    """
    Return a dictionary of Experiment objects representing all the test cases.
    """

    # Path to top level MOM-examples
    exps = {}
    for path, _, filenames in os.walk(_mom_examples_path):
        for fname in filenames:
            if fname == 'input.nml':
                id = exp_id_from_path(path)
                exps[id] = Experiment(id)
    return exps

# A dictionary of available experiments.
experiment_dict = discover_experiments()
