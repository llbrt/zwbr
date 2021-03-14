def is_id_set(bit_field, bit_id):
    """ Tells if the bit of an id is set.
    Id 1 => byte 0/bit 0, id 2 => byte 0/bit 1 and so on."""
    count = len(bit_field)
    if bit_id > (count * 8):
        return False
    bit_pos = bit_id - 1
    index = int(bit_pos / 8)
    shift = bit_pos % 8
    return bit_field[index] & (1 << shift) != 0
