
import socket
import os

def get_exec_prefix(model, exp_name):
    """
    Return a prefix needed to execute the given experiment.

    model is the model configuration, e.g. ice_ocean_SIS2 or ocean_only
    exp_name is the experiment name, e.g. Baltic or global_ALE/z
    """

    ncpus = 2
    pbs_ncpus = os.getenv('PBS_NCPUS')
    if pbs_ncpus is not None:
        ncpus = int(pbs_ncpus)

    exec_prefix = 'mpirun -n {}'.format(ncpus)

    pbs_o_host = os.getenv('PBS_O_HOST')
    if pbs_o_host is not None and 'gaea' in pbs_o_host:
        exec_prefix = 'aprun -n {}'.format(ncpus)

    return exec_prefix
