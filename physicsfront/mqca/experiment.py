##
# Copyright 2023 Physics Front LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

Run = __import__ ('collections').namedtuple ('Run', 'qc job result memory counts')

def bb84 (source_name = 'secret_quantume_key', # <<< pylint: disable=W0613
          party1 = 'amar', party2 = 'juan', # pylint: disable=W0613
          party3 = 'evil_hacker', basis12 = 'random', # pylint: disable=W0613
          barrier = 'auto', simulate = True,
          shots = 10000, seed = 100, keys = None, # pylint: disable=W0613
          job = None): # pylint: disable=W0613
    """
    Sets up a BB84 experiment, runs it using :func:`run`, and returns the
    result.

    This function is a simple wrapper around
    :func:`~physicsfront.mqca.qc_bb84` and :func:`run`.  All arguments from
    ``simulate`` and after are passed to :func:`run`, while all other
    arguments are used for :func:`~physicsfront.mqca.qc_bb84`.

    The two arguments that are processed by this function, instead of merely
    being passed through, are ``basis12`` and ``barrier``.

    :param basis:  If 'random' (default) and ``simulate`` is false, then
        this function will create two quantum circuits, not one, due to the
        fact that qasm3/dynamic-circuit does not work with qiskit (as of Jan
        2023, at least).

    :param barrier:  By default, this argument is set to true if ``simulate``
        and false otherwise.  Using barriers while not simulating will
        result in unexpected/wrong results.  So, the default value 'auto'
        must not be modified without a really good reason to do so.
    """
    dargs1 = dict (** locals ())
    if barrier == 'auto':
        dargs1 ['barrier'] = barrier = bool (simulate)
    if not simulate and barrier:
        import sys
        print ("** WARNING: barrier is set for quantum computer run---this "
               "can easily produce an unexpected result.", file = sys.stderr)
    dargs2 = dict ((k, dargs1.pop (k)) for k
                   in ('simulate', 'shots', 'seed', 'keys', 'job'))
    from physicsfront.mqca import qc_bb84 # pylint: disable=E0401,E0611
    if not simulate and basis12 == 'random':
        # workaround (since qasm3 (dynamic circuit) does not work yet)
        del dargs1 ['basis12']
        dargs2 ['shots'] = int (dargs2 ['shots'] / 2)
        qc = (qc_bb84 (basis12 = 'z', ** dargs1),
              qc_bb84 (basis12 = 'x', ** dargs1))
    else:
        qc = qc_bb84 (** dargs1)
    return run (qc, ** dargs2)
# >>>
def run (qc, simulate = True, shots = 10000, seed = 100, keys = None, # <<<
         job = None):
    """
    Runs ``qc`` (which can be a quantum circuit or a tuple/list of quantum
    circuits) and returns a :func:`~collections.namedtuple` :const:`Run`
    instance.

    A :const:`Run` instance contains fields 'qc', 'job', 'result', 'memory',
    'counts'.  If the input ``qc`` is a tuple/list, then all fields will
    hold tuple values.  Else, all fields will hold appropriate single object
    values.

    :param job:  If provided, then it must be a job or a sequence of jobs
        corresponding one-to-one to ``qc``.  In this case, the three
        arguments ``simulate``, ``shots``, and ``seed`` are not used since
        they are used only when jobs are created anew.

    :param keys:  Passed to :func:`~physicsfront.qiskit.gather_counts` when
        collecting counts after collecting run results.
    """
    # pylint: disable=E0401,E0611,W0611
    from physicsfront.qiskit import (gather_counts, run_quantum_computer,
                                     run_quantum_simulator)
    from collections import Counter
    from random import randint
    def get_clspecs_predicate (qc):
        dargs = getattr (qc, '_dargs', {})
        clspecs = ()
        predicate = None
        if 'party1' in dargs and 'party2' in dargs:
            clspecs = (dargs ['party1'] + '_rec', dargs ['party2'] + '_rec')
            if dargs.get ('basis12') == 'random':
                predicate = (dargs ['party1'] + '_pre| == ' +
                             dargs ['party2'] + '_pre|')
        return clspecs, predicate
    shots_counter = None
    multiple_qc = isinstance (qc, (tuple, list))
    if multiple_qc:
        qc = tuple (qc)
        N = len (qc) - 1
        assert N >= 0
        cp = tuple (get_clspecs_predicate (q) for q in qc)
        if job is None:
            shots_counter = Counter (randint (0, N) for i in range (shots))
    else:
        cp = (get_clspecs_predicate (qc),)
        qc = (qc,)
        if job is None:
            shots_counter = Counter ({0: shots})
        else:
            job = (job,)
    # pylint: enable=E0401,E0611,W0611
    dargs_runf = {'seed': seed} if simulate else {}
    runf = run_quantum_simulator if simulate else run_quantum_computer
    if job is None:
        j = tuple (runf (q, shots = shots_counter [i], ** dargs_runf)
                   for i, q in enumerate (qc))
    else:
        assert len (job) == len (qc)
        j = tuple (job)
    r = tuple (job.result () for job in j)
    m = tuple (res.get_memory () for res in r)
    counts = tuple ((lambda clspecs = c_p [0], predicate = c_p [1],
                     keys = keys, res = res: gather_counts (res, * clspecs,
                     predicate = predicate, keys = keys))
                    for c_p, res in zip (cp, r))
    args = qc, j, r, m, counts
    if multiple_qc:
        return Run (* args)
    return Run (* (a [0] for a in args))
# >>>
