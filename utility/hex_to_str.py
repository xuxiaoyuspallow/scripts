
def hex_to_str(hex):
    pass


def str_to_hex(str):
    result = '0x'
    for s in str:
        result += hex(ord(s))[2:]
    return result

