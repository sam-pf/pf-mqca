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

def qc_entangled_two_qubits (kind = 1, statevector = False, # <<<
                             measure = True):
    """
    :param statevector:  Only for simulator run.
    """
    from qiskit import QuantumCircuit # pylint: disable=W0406,E0611
    if statevector:
        # This is for 'qc.save_statevector'.
        from qiskit.providers.aer import Aer # pylint: disable=E0401,E0611,W0611
    qc = QuantumCircuit (2)
    if kind == 0: # symmetric Bell sate: |00> + |11>
        iv0 = [1, 0]
        iv1 = [1, 0]
    elif kind == 1: # EPR: -|01> + |10>
        iv0 = [0, 1]
        iv1 = [0, 1]
    elif kind == 2: # |00> - |11>
        iv0 = [0, 1]
        iv1 = [1, 0]
    elif kind == 3: # |01> + |10>
        iv0 = [1, 0]
        iv1 = [0, 1]
    else:
        iv0, iv1 = kind
    qc.initialize (iv0, 0) # pylint: disable=E1101
    qc.initialize (iv1, 1) # pylint: disable=E1101
    qc.h (0)
    qc.cx (0, 1)
    if statevector:
        qc.save_statevector () # pylint: disable=E1101
        ##
        # Later, do 'j.result ().get_statevector ()' where j is job (returned
        # by run_quantum_simulator)
        ##
    if measure:
        qc.measure_all ()
    return qc
# >>>
def qc_for_random_bits (statevector = False, measure = True): # <<<
    """
    :param statevector:  Only for simulator run.
    """
    from qiskit import QuantumCircuit # pylint: disable=W0406,E0611
    if statevector:
        # This is for 'qc.save_statevector'.
        from qiskit.providers.aer import Aer # pylint: disable=E0401,E0611,W0611
    qc = QuantumCircuit (1)
    qc.initialize ([1, 0], 0) # pylint: disable=E1101
    qc.h (0)
    if statevector:
        qc.save_statevector () # pylint: disable=E1101
    if measure:
        qc.measure_all ()
    return qc
# >>>
