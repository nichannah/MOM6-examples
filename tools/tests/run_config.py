
import socket
import os

def get_exec_prefix(model, exp_name, variation):
    """
    Return a prefix needed to execute the given experiment.

    model is the model configuration, e.g. ice_ocean_SIS2 or ocean_only
    exp_name is the experiment name, e.g. Baltic or global_ALE
    variation is the a variation on the experiment, e.g. z, layer. 
    """

    ncpus = 384
    if 'benchmark' in exp_name or 'double_gyre' in exp_name:
        ncpus = 1
    exec_prefix = 'mpirun -n {}'.format(ncpus)

    pbs_o_host = os.getenv('PBS_O_HOST')
    if pbs_o_host is not None and 'gaea' in pbs_o_host:
        exec_prefix = 'aprun -n {}'.format(ncpus)

    return exec_prefix
