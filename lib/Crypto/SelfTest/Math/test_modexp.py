#
#  SelfTest/Math/test_modexp.py: Self-test for module exponentiation
#
# ===================================================================
#
# Copyright (c) 2017, Helder Eijs <helderijs@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ===================================================================

"""Self-test for the custom module exponentiation"""

import unittest

from Crypto.SelfTest.st_common import list_test_cases

from Crypto.Util.number import long_to_bytes, bytes_to_long

from Crypto.Util.py3compat import *

from Crypto.Util._raw_api import (load_pycryptodome_raw_lib,
                                  create_string_buffer,
                                  get_raw_buffer,
                                  c_size_t, expect_byte_string)


c_defs = """
int monty_pow(const uint8_t *base,
               const uint8_t *exp,
               const uint8_t *modulus,
               uint8_t       *out,
               size_t len,
               uint64_t seed);
"""


_raw_montgomery = load_pycryptodome_raw_lib("Crypto.Math._montgomery", c_defs)


class ExceptionModulus(ValueError):
    pass

def monty_pow(base, exp, modulus):
    max_len = len(long_to_bytes(max(base, exp, modulus)))

    base_b, exp_b, modulus_b = [ long_to_bytes(x, max_len) for x in
                                 (base, exp, modulus) ]

    out = create_string_buffer(max_len)
    error = _raw_montgomery.monty_pow(
                base_b,
                exp_b,
                modulus_b,
                out,
                c_size_t(max_len),
                32
                )

    if error == 2:
        raise ExceptionModulus()
    if error:
        raise ValueError("monty_pow failed with error: %d" % error)

    result = bytes_to_long(get_raw_buffer(out))
    return result

exponent1 = 0x2ce0af628901460a419a08ef950d498b9fd6f271a1a52ac293b86fe5c60efe8e8ba93fa1ebe1eb3d614d2e7b328cb60a2591440e163441a190ecf101ceec245f600fffdcf3f5b3a17a7baeacb96a424db1d7ec985e8ec998bb479fecfffed6a75f9a90fc97062fd973303bce855ad7b8d8272a94025e8532be9aabd54a183f303538d2a7e621b4131d59e823a4625f39bd7d518d7784f7c3a8f19061da74974ff42fa1c063dec2db97d461e291a7d6e721708a5229de166c1246363372854e27f3f08ae274bc16bfd205b028a4d81386494433d516dfbb35f495acba5e4e1d1843cb3c3129b6642a85fc7244ce5845fac071c7f622e4ee12ac43fabeeaa0cd01
modulus1 = 0xd66691b20071be4d66d4b71032b37fa007cfabf579fcb91e50bfc2753b3f0ce7be74e216aef7e26d4ae180bc20d7bd3ea88a6cbf6f87380e613c8979b5b043b200a8ff8856a3b12875e36e98a7569f3852d028e967551000b02c19e9fa52e83115b89309aabb1e1cf1e2cb6369d637d46775ce4523ea31f64ad2794cbc365dd8a35e007ed3b57695877fbf102dbeb8b3212491398e494314e93726926e1383f8abb5889bea954eb8c0ca1c62c8e9d83f41888095c5e645ed6d32515fe0c58c1368cad84694e18da43668c6f43e61d7c9bca633ddcda7aef5b79bc396d4a9f48e2a9abe0836cc455e435305357228e93d25aaed46b952defae0f57339bf26f5a9


class TestModExp(unittest.TestCase):

    def test_small(self):
        self.assertEqual(1, monty_pow(11,12,19))

    def test_large_1(self):
        base = 0xfffffffffffffffffffffffffffffffffffffffffffffffffff
        expected = pow(base, exponent1, modulus1)
        result = monty_pow(base, exponent1, modulus1)
        self.assertEqual(result, expected)

    def test_zero_exp(self):
        base = 0xfffffffffffffffffffffffffffffffffffffffffffffffffff
        result = monty_pow(base, 0, modulus1)
        self.assertEqual(result, 1)

    def test_zero_base(self):
        result = monty_pow(0, exponent1, modulus1)
        self.assertEqual(result, 0)

    def test_zero_modulus(self):
        base = 0xfffffffffffffffffffffffffffffffffffffffffffffffffff
        self.assertRaises(ExceptionModulus, monty_pow, base, exponent1, 0)
        self.assertRaises(ExceptionModulus, monty_pow, 0, 0, 0)

    def test_larger_exponent(self):
        base = 0xfffffffffffffffffffffffffffffffffffffffffffffffffff
        expected = pow(base, modulus1 << 64, modulus1)
        result = monty_pow(base, modulus1 << 64, modulus1)
        self.assertEqual(result, expected)

    def test_even_modulus(self):
        base = 0xfffffffffffffffffffffffffffffffffffffffffffffffffff
        self.assertRaises(ExceptionModulus, monty_pow, base, exponent1, modulus1-1)


def get_tests(config={}):
    tests = []
    tests += list_test_cases(TestModExp)
    return tests


if __name__ == '__main__':
    suite = lambda: unittest.TestSuite(get_tests())
    unittest.main(defaultTest='suite')