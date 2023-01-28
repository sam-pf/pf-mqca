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

from . import experiment

def qc_bb84 (source_name = 'secret_quantume_key', party1 = 'amar', # <<<
             party2 = 'juan', party3 = 'evil_hacker', basis12 = 'random',
             barrier = True):
    qc = qc_entangle_two_qubits (name = source_name)
    qc1 = qc_measure_qubit (name = party1, basis = basis12)
    qc2 = qc_measure_qubit (name = party2, basis = basis12)
    qc3 = qc_eavesdrop_qubit (name = party3) if party3 else None
    instructions = []
    if qc3:
        instructions.append ((qc3, [(1, 0)], barrier))
    instructions.append ({'qc': qc1, 'wiring': [(0, 0)], 'barrier': barrier})
    instructions.append (((qc2, [(1, 0)]), {'barrier': barrier}))
    from physicsfront.qiskit import wire # pylint: disable=E0401,E0611
    return wire (qc, * instructions)
# >>>
def qc_eavesdrop_qubit (name = 'evil_hacker'): # <<<
    """
    Creates a quantum circuit to measure a qubit.

    The circuit will contain a quantum register of length 1, which is tapped
    (and thus will be modified by measurement), and a classical register of
    length 1, which stores the measurment outcome.
    """
    from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
    qr = QuantumRegister (1, name = name + '_qubit')
    cr = ClassicalRegister (1, name = name + '_listens')
    qc = QuantumCircuit (qr, cr)
    qc.measure (qr, cr)
    return qc
# >>>
def qc_entangle_two_qubits (name = 'secret_quantume_key', kind = 1, # <<<
                            statevector = False):
    """
    Creates a quantum circuit with entangled two qubits. The entanglement
    will be the maximum entanglement if ``kind`` is left as the default
    value, or chosen from four integer choices (0, 1, 2, 3).

    :param name:  This is the name of the register for the two qubits.  To
        disable the register, pass a false value.  To have two registers,
        instead of one, pass a 2-tuple of names.

    :param kind:  0, 1 (default), 2, 3.

        The four integer values correspond to the four Bell states prepared
        by this circuit through entanglement.

        Up to a normalization constant, they are the following.

            kind == 0: |00> + |11>
            kind == 1: |01> - |10> (singlet EPR; this is the default)
            kind == 2: |00> - |11>
            kind == 3: |01> + |10>

    :param statevector:  Only for simulator run.  The state vector will be
        saved after initialization.
    """
    from qiskit import QuantumCircuit, QuantumRegister # pylint: disable=W0406,E0611
    if statevector:
        # This is for 'qc.save_statevector'.
        from qiskit.providers.aer import Aer # pylint: disable=E0401,E0611,W0611
    if name:
        args = []
        if type (name) == str:
            args.append (QuantumRegister (2, name = name))
        else:
            name1, name2 = name
            args.append (QuantumRegister (1, name = name1))
            args.append (QuantumRegister (1, name = name2))
    else:
        args = [2]
    qc = QuantumCircuit (* args)
    if kind == 0: # symmetric Bell sate: |00> + |11>
        iv0 = (1, 0)
        iv1 = (1, 0)
    elif kind == 1: # EPR: -|01> + |10>
        iv0 = (0, 1)
        iv1 = (0, 1)
    elif kind == 2: # |00> - |11>
        iv0 = (0, 1)
        iv1 = (1, 0)
    elif kind == 3: # |01> + |10>
        iv0 = (1, 0)
        iv1 = (0, 1)
    else:
        raise ValueError (f'Invalid value {kind!r} passed for kind.')
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
    return qc
# >>>
def qc_for_random_bits (name = 'control', measure = 'random', # <<<
                        statevector = False):
    """
    Creates a quantum circuit consisting of one qubit, which is maximally
    superposed to create a sequence of random bits when measured.

    :param name: The name of the quantum register for the qubit.  To disable
        the register, pass a false value.

    :param statevector:  Only for simulator run.  The state vector will be
        saved after initialization.

    :param measure:  By default, the random bit will be recorded in the
        classical register named 'random.'  This name may be changed. To
        disable the register (and just call measure_all for measurement),
        pass a true value which is _not_ a string.

        To disable the measurement, pass any false value.
    """
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister # pylint: disable=W0406,E0611
    if statevector:
        # This is for 'qc.save_statevector'.
        from qiskit.providers.aer import Aer # pylint: disable=E0401,E0611,W0611
    if name:
        args = [QuantumRegister (1, name = name)]
    else:
        args = [1]
    measure_src = args [0]
    if measure:
        if type (measure) == str:
            args.append (ClassicalRegister (1, name = measure))
            measure_tgt = args [-1]
        else:
            measure_tgt = None
    else:
        measure_src = None
    qc = QuantumCircuit (* args)
    qc.initialize ((100, 0), 0) # pylint: disable=E1101
    qc.h (0)
    if statevector:
        qc.save_statevector () # pylint: disable=E1101
    if measure_src:
        if measure_tgt is None:
            qc.measure_all ()
        else:
            qc.measure (measure_src, measure_tgt)
    return qc
# >>>
def qc_measure_qubit (name = 'amal', basis = 'random'): # <<<
    """
    Creates a quantum circuit for measuring a qubit using basis 'z', 'x', a
    random choice between the two.

    The circuit will have two registers.
    - The first quantum register of length 1, containing the qubit to measure.
    - The last classical register of length 1, to store the measurement result.

    In addition, there will be two more registers if bais == 'random'.
    - The second quantum register of length 1, to generate random bit.
    - The first classical register of length 1, to store that random bit.  When
    this bit is true, then the 'x' basis applies, while when this bit is
    false, then the 'z' basis applies.
    """
    from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
    qr1 = QuantumRegister (1, name = name + '_qubit')
    cr1 = ClassicalRegister (1, name = name + '_receives')
    if basis == 'random':
        qr1c = QuantumRegister (1, name = name + '_prepares')
        cr1c = ClassicalRegister (1, name = name + '_prep_bit')
        qc = QuantumCircuit (qr1, qr1c, cr1c, cr1)
        qc.initialize ((100, 0), qr1c) # pylint: disable=E1101
        qc.h (qr1c)
        qc.measure (qr1c, cr1c)
        qc.h (qr1).c_if (cr1c, 1) # dynamic circuit
    elif basis == 'z':
        qc = QuantumCircuit (qr1, cr1)
    elif basis == 'x':
        qc = QuantumCircuit (qr1, cr1)
        qc.h (qr1)
    else:
        raise ValueError ("Invalid value for basis: not one of 'z', 'x', "
                          "'random'")
    qc.measure (qr1, cr1)
    return qc
# >>>
