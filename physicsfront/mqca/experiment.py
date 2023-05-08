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

class Run (object): # <<<

    def __init__ (self, qc, job, take_value_if_single = False):
        assert type (qc) is tuple
        assert type (job) is tuple
        assert len (qc) == len (job)
        self._qc = qc
        self._job = job
        self._take_value_if_single = take_value_if_single
        self._result = self._memory = self._counts = None

    def __len__ (self):
        return len (self._qc)

    def _get_prop_value (self, a, required = False):
        if not required and a is None:
            return
        assert type (a) is tuple
        assert len (a) == len (self)
        if self._take_value_if_single and len (a) == 1:
            return a [0]
        return a

    @property
    def counts (self):
        return self._get_prop_value (self._counts)

    @property
    def job (self):
        return self._get_prop_value (self._job, required = True)

    @property
    def memory (self):
        return self._get_prop_value (self._memory)

    @property
    def qc (self):
        return self._get_prop_value (self._qc, required = True)

    @property
    def result (self):
        return self._get_prop_value (self._result)

    @property
    def is_finalized (self):
        r = self._result
        m = self._memory
        c = self._counts
        if r is None and m is None and c is None:
            return False
        elif r is not None and m is not None and c is not None:
            return True
        else:
            raise ValueError ("** Error: final props are partially assigned.")

    def finalize (self, keys = None, redo = False): # <<<
        """
        Gets the final result for this run.

        When finalized, all three properties, ``result``, ``memory``, and
        ``counts`` will return non-``None`` values.

        :param keys:  Passed to :func:`~physicsfront.qiskit.gather_counts`
            when collecting counts after collecting run results.
        """
        from physicsfront.qiskit import gather_counts # pylint: disable=E0401
        import sys
        jobs = self._job
        for job in jobs:
            status = job.status ()
            if status.name != 'DONE':
                # pylint: disable=W0719
                raise Exception ("Can't get result for a job with status = "
                                 f"{status}.")
        if self.is_finalized and not redo:
            print ("""This Run object has already been finalized.
There is nothing to do.

To re-finalize, you can pass a true value for the 'redo' argument.""",
                   file = sys.stderr)
            return
        # TODO: add an option to customize this getter
        def get_clspecs_predicate (qc):
            dargs = getattr (qc, '_dargs', {})
            clspecs = ()
            predicate = None
            if 'party1' in dargs and 'party2' in dargs:
                clspecs = (dargs ['party1'] + '_rec', dargs ['party2'] +
                           '_rec')
                if dargs.get ('basis12') == 'random':
                    predicate = (dargs ['party1'] + '_pre| == ' +
                                 dargs ['party2'] + '_pre|')
            return clspecs, predicate
        qc = self._qc
        r = tuple (job.result () for job in jobs)
        m = tuple (res.get_memory () for res in r)
        cp = tuple (get_clspecs_predicate (q) for q in qc)
        ##
        # counts are functions (lambda forms); maybe keys can be retweaked
        # later on?
        ##
        counts = tuple ((lambda clspecs = c_p [0], predicate = c_p [1],
                         keys = keys, res = res: gather_counts (res, * clspecs,
                         predicate = predicate, keys = keys))
                        for c_p, res in zip (cp, r))
        self._result = r
        self._memory = m
        self._counts = counts
    # >>>
    def monitor (self): # <<<
        import sys
        if self.is_finalized:
            print ("This Run has been finalized already (nothing to monitor).",
                   file = sys.stderr)
            return
        from physicsfront.qiskit import jobs_monitor # pylint: disable=E0401
        return jobs_monitor (self._job)
    # >>>

# >>>

def bb84 (source_name = 'secret_quantume_key', # <<< pylint: disable=W0613
          party1 = 'amar', party2 = 'juan', # pylint: disable=W0613
          party3 = 'evil_hacker', basis12 = 'random', # pylint: disable=W0613
          barrier = 'auto', simulate = True,
          shots = 10000, seed = 100): # pylint: disable=W0613
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
                   in ('simulate', 'shots', 'seed'))
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
def run (qc, simulate = True, shots = 10000, seed = 100): # <<<
    """
    Runs ``qc`` (which can be a quantum circuit or a tuple/list of quantum
    circuits) and returns a tuple of submitted jobs.

    Returns a :class:`Run` instance that must be finalized to get results
    when it is know that all jobs finished successfully.
    """
    # pylint: disable=E0401,E0611,W0611
    from physicsfront.qiskit import (run_quantum_computer,
                                     run_quantum_simulator)
    from collections import Counter
    from random import randint
    shots_counter = None
    as_tuple = isinstance (qc, (tuple, list))
    if as_tuple:
        qc = tuple (qc)
        N = len (qc) - 1
        assert N >= 0
        shots_counter = Counter (randint (0, N) for i in range (shots))
    else:
        qc = (qc,)
        shots_counter = Counter ({0: shots})
    # pylint: enable=E0401,E0611,W0611
    dargs_runf = {'seed': seed} if simulate else {}
    runf = run_quantum_simulator if simulate else run_quantum_computer
    jobs = tuple (runf (q, shots = shots_counter [i], ** dargs_runf)
                  for i, q in enumerate (qc))
    return Run (qc, jobs, take_value_if_single = not as_tuple)
# >>>
