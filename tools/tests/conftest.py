
import os

import pytest
from dump_all_diagnostics import dump_diags
from experiment import experiment_dict, exp_id_from_path

def pytest_addoption(parser):
    parser.addoption('--exps', default=None,
                     help="""comma-separated no spaces list of experiments to
                             pass to test functions. Experiments are described
                             in the form <model_name>/<exp_name>. Also you must use the '='
                             sign otherwise py.test gets confused, e.g:
                             $ py.test --exps=ice_ocean_SIS2/Baltic,ocean_only/benchmark""")
    parser.addoption('--fast', action='store_true', default=False,
                     help="""Run a fast subset of tests.""")

def pytest_generate_tests(metafunc):
    """
    Parameterize tests.
    """
    def select_exps(metafunc):
        if metafunc.config.option.fast:
            # Run a fast subset of the experiments.
            exps = [experiment_dict['ocean_only/double_gyre']]
        elif metafunc.config.option.exps is not None:
            # Only run on the given experiments.
            exps = []
            for e in metafunc.config.option.exps.split(','):
                # Replace '-' with '/'. Jenkins does the wrong thing with these.
                e = e.replace('-', '/')
                if not experiment_dict.has_key(e):
                    if experiment_dict.has_key('ocean_only/' + e):
                        e = 'ocean_only/' + e
                    elif experiment_dict.has_key('ice_ocean_SIS2/' + p):
                        e = 'ice_ocean_SIS2/' + e
                exps.append(experiment_dict[e])
        else:
            # Run tests on all experiments.
            exps = experiment_dict.values()
        return exps

    if 'exp' in metafunc.fixturenames:
        exps = select_exps(metafunc)
        metafunc.parametrize('exp', exps, indirect=True)

    if 'prerun_exp' in metafunc.fixturenames:
        exps = select_exps(metafunc)
        metafunc.parametrize('prerun_exp', exps, indirect=True)

    if 'model' in metafunc.fixturenames:
        models = ['ocean_only']
        metafunc.parametrize('model', models, indirect=True)

    if 'build' in metafunc.fixturenames:
        builds = ['debug', 'repro']
        metafunc.parametrize('build', builds, indirect=True)

    if 'compiler' in metafunc.fixturenames:
        compilers = ['gnu', 'intel']
        metafunc.parametrize('compiler', compilers, indirect=True)

@pytest.fixture
def model(request):
    return request.param

@pytest.fixture
def build(request):
    return request.param

@pytest.fixture
def compiler(request):
    return request.param

    if 'prerun_exp' in metafunc.fixturenames:
        exps = select_exps(metafunc)
        metafunc.parametrize('prerun_exp', exps, indirect=True)

    if 'model' in metafunc.fixturenames:
        if metafunc.config.option.slow:
            models = ['ocean_only', 'ice_ocean_SIS2']
        else:
            # Default is to run on a fast subset
            models = ['ocean_only']
        metafunc.parametrize('model', models, indirect=True)

    if 'build' in metafunc.fixturenames:
        builds = ['debug', 'repro']
        metafunc.parametrize('build', builds, indirect=True)

    if 'compiler' in metafunc.fixturenames:
        compilers = ['gnu', 'intel']
        metafunc.parametrize('compiler', compilers, indirect=True)

@pytest.fixture
def model(request):
    return request.param

@pytest.fixture
def build(request):
    return request.param

@pytest.fixture
def compiler(request):
    return request.param

@pytest.fixture
def exp(request):
    """
    Fixture for tests than need an experiment which has not been run.
    """
    return request.param

@pytest.fixture
def prerun_exp(request):
    """
    Fixture for tests that need an experiment which has not been run.
    """
    exp = request.param

    # Run the experiment to get latest code changes. This will do nothing if
    # the experiment has already been run.
    exp.run()
    # Dump all available diagnostics, if they haven't been already.
    if not exp.has_dumped_diags:
        # Before dumping we delete old ones if they exist.
        diags = exp.get_available_diags()
        for d in diags:
            try:
                os.remove(d.output)
            except OSError:
                pass

        dump_diags(exp, diags)
        exp.has_dumped_diags = True
    return exp

def restore_after_test():
    """
    Restore experiment state after running a test.

    - The diag_table files needs to be switched back (?)
    """
    pass

@pytest.fixture(scope='module')
def prepare_to_test():
    """
    Called once for a test module.

    - Make a backup of the diag_table, to be restored later. (?)
    """
    pass
