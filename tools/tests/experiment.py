
from __future__ import print_function

import sys
import os
import re
import shlex
import string
import subprocess as sp
import run_config as rc
from model import mkdir_p

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
    Return an experiment id string of the form <model>/<exp> from a
    full path.
    """
    path = os.path.normpath(path)
    path = path.replace(_mom_examples_path, '')
    # Remove possible '/' from front and back.
    return string.strip(path, '/')

class Experiment:

    def __init__(self, id):
        """
        Python representation of an experiment/test case.

        The id is a string of the form <model>/<exp>
        """

        id = id.split('/')
        self.model = id[0]
        self.name = ''.join(id[1:])
        self.path = os.path.join(_mom_examples_path, self.model, self.name)

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

        # Whether this experiment has been run/built. Want to try to avoid
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

    def get_model(self):
        """
        Return model used to run this experiment.
        """
        return self.model

    def get_path(self):
        """
        Return path to this experiment.
        """
        return self.path

    def run(self, build='repro', compiler='gnu'):
        """
        Run the experiment if it hasn't already.
        """
        if self.has_run:
            return 0
        else:
            ret, _, _ = self.force_run(build, compiler)
            return ret

    def force_run(self, build='repro', compiler='gnu', fake_it=False):
        """
        Run the experiment, return error code and the command used.
        """
        rel_path = 'build/{}/{}/{}/MOM6'.format(compiler, self.model, build)
        exec_path = os.path.join(_mom_examples_path, rel_path)
        assert(os.path.exists(exec_path))

        ret = 0
        saved_path = os.getcwd()
        os.chdir(self.path)
        mkdir_p('RESTART')
        try:
            prefix = rc.get_exec_prefix(self.model, self.name)
            cmd = prefix + ' ' + exec_path
            if not fake_it:
                print('Executing ' + cmd)
                output = sp.check_output(shlex.split(cmd), stderr=sp.STDOUT)
                self.has_run = True
        except sp.CalledProcessError as e:
            ret = e.returncode
            print(e.output, file=sys.stderr)
        finally:
            os.chdir(saved_path)
        return ret, prefix, exec_path

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
    for path, dirs, filenames in os.walk(_mom_examples_path):
        for fname in filenames:
            if fname == 'input.nml' and 'common' not in path:
                id = exp_id_from_path(path)
                print(id)
                exps[id] = Experiment(id)
    return exps

# A dictionary of available experiments.
experiment_dict = discover_experiments()
