import binascii
import random
from ecdsa.ecdsa import generator_secp256k1

g = generator_secp256k1
p = g.curve().p()
order = g.order()

def string_to_number(string):
    return int(binascii.hexlify(string), 16)

def hexed_to_number(hexed):
    return int(hexed, 16)

def orderlen(order):
    return (1 + len("%x" % order)) // 2  # bytes

def number_to_string(num, order):
    ll = orderlen(order)
    fmt_str = "%0" + str(2 * ll) + "x"
    return fmt_str % num

def tron_sign(message, private: bytearray):
  d = hexed_to_number(private)
  k = string_to_number(bytes(random.sample(range(0, 256), 32))) % order
  e = hexed_to_number(message)

  point = g * k

  s = (pow(k, -1, order) * (e + d * point.x())) % order

  ss = number_to_string(point.x() % order, order) + number_to_string(s, order)
  rec_id = 27 + point.y() % 2

  return ss + number_to_string(rec_id, 2)
