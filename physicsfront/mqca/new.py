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

"""WIP"""

class RandomBits (object):

    def generate (self, n = 10):
        pass

class RandomBitsQ (RandomBits):

    def __init__ (self):
        pass

class RandomBitsC (RandomBits):

    def __init__ (self, seed = 3):
        pass

class QBitBasis (object):

    def __init__ (self, definition = 'Z'):
        """
        :param definition: 'Z', 'X', 'Z,X', or a QBitBasis instance
            already with these definitions.

            'Z,X' means a random choice between 'Z' and 'X'.
            'X,Z' is also accepted, but is immediately converted to 'Z,X'.
        """
        if definition == 'X,Z':
            definition = 'Z,X'
        if isinstance (definition, QBitBasis):
            definition = definition.definition
        assert definition in ('Z', 'X', 'Z,X')
        self._definintion = definition

    def definition (self):
        return self._definintion

class InfoSender (object): # sender *and* keeper of qbits or bits

    def __init__ (self, nmax = 4096):
        self._kept = ()
        self._sent = ()
        assert type (nmax) == int and nmax > 0 and nmax <= 10000
        self._nmax = nmax

    @property
    def kept (self): # all bits kept, cumulative
        ans = self._kept
        assert type (ans) == tuple
        return ans

    @property
    def n_done (self):
        ans = len (self.kept)
        assert ans == len (self.sent)
        return ans

    @property
    def nmax_left (self):
        n_done = self.n_done
        ans = self._nmax - n_done
        return 0 if ans < 0 else ans

    def send (self, n = 1):
        raise NotImplementedError

    @property
    def sent (self): # all bits sent, cumulative
        ans = self._sent
        assert type (ans) == tuple
        return ans

class Eavesdropper (object):

    def __init__ (self, basis = 'X'):
        self._basis = QBitBasis (basis)

    @property
    def basis (self):
        return self._basis

    def eavesdrop (self, sent):
        pass

class InfoSenderC (InfoSender):

    def __init__ (self, bits, nmax = 4096):
        self._bits = iter (bits)
        super (InfoSenderC, self).__init__ (nmax = nmax)

    def send (self, n = 1):
        """
        Sends ``n`` bits.  If ``n == 0``, then it means sending all remaining
        bits.

        :returns:  0 or 1 if only one bit was sent or a list of 0 or 1 if
            the number of bits sent is not one.
        """
        assert type (n) == int and n >= 0
        t = []
        t_append = t.append
        assert len (self._kept)
        n_more = self._nmax - len (self._kept)
        if n > n_more:
            raise OverflowError ("Cannot send: n=%d (> %d, the maximum "
                                 "left allowed)" % (n, n_more))
        n_sent = 0
        for b in self._bits:
            if n_sent >= n_more:
                # This happens only when n = 0.
                assert not n
                raise OverflowError ("The maximum number of bits sendable "
                                     "(%d) has been reached." % (self._nmax))
            if b == '0' :
                b = 0
            elif b == '1':
                b = 1
            assert b == 0 or b == 1
            t_append (b)
            n_sent += 1
            if n_sent == n:
                break
        if n > n_sent:
            raise Exception ("Underflow error---number of missing bits: %d"
                             % (n - n_sent,))
        t = tuple (t)
        self._kept += t
        self._sent += t
        return t [0] if n_sent == 1 else t

class InfoSenderQ (InfoSender): # pylint: disable=W0223

    def __init__ (self, senderbasis = 'Z', receiverbasis = 'Z', nmax = 4096):
        self._senderbasis = QBitBasis (senderbasis)
        self._receiverbasis = QBitBasis (receiverbasis)
        super (InfoSenderQ, self).__init__ (nmax = nmax)

    @property
    def receiverbasis (self):
        return self._receiverbasis

    @property
    def senderbasis (self):
        return self._senderbasis

class InfoSenderQ1 (InfoSenderQ): # simple qbit sender # pylint: disable=W0223
    pass

class InfoSenderQ2 (InfoSenderQ): # entangled qbit sender # pylint: disable=W0223
    pass

class Setting (object):

    def __init__ (self, infosender, eavesdropper = None):
        assert isinstance (infosender, InfoSender)
        self._infosender = infosender
        if eavesdropper:
            assert isinstance (eavesdropper, Eavesdropper)
        self._eavesdropper = eavesdropper
        self._received = ()

    @property
    def eavesdropper (self):
        return self._eavesdropper

    @property
    def infosender (self):
        return self._infosender

    @property
    def kept (self): # all (q)bits kept, cumulative
        return self.infosender.kept

    @property
    def received (self): # all (q)bits received, cumulative
        return self._received

    def send (self, n = 1):
        assert type (n) == int and n > 0
        eavesdrop = self.eavesdropper
        if eavesdrop:
            eavesdrop = eavesdrop.eavesdrop
            assert (eavesdrop)
        send = self.infosender.send
        if eavesdrop:
            if n == 1:
                rv = eavesdrop (send (n = 1))
            else:
                rv = tuple (eavesdrop (send (n = 1)) for i in range (n))
        else:
            rv = send (n = n)
        ##
        # Data types: 'send', 'eavesdrop'
        #
        # 1. send (n = 1) must return a non-tuple.
        # 2. send (n > 1) must return a tuple, consisting of non-tuples.
        # 3. eavesdrop should take a non-tuple and return a non-tuple.
        ##
        if n == 1:
            assert type (rv) != tuple
            self._received += (rv,)
        else:
            assert type (rv) == tuple
            for e in rv:
                assert type (e) != tuple
            self._received += rv
        return rv

    @property
    def sent (self): # all (q)bits sent, cumulative
        return self.infosender.sent
