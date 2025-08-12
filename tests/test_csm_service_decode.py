from app.services.csm_service import CsmService


def test_decode_batch_layout_64_64_128():
    # Layout: [id:64][count:64][next:128]
    node_id = 0xABCDEF
    count = 0x12345678
    next_index = 0xdeadbeefcafebabe1234567890abcdef
    hi = (node_id << 64) | count
    packed = (hi << 128) | (next_index & ((1 << 128) - 1))
    got_id, got_count = CsmService._decode_batch(packed)
    assert got_id == node_id
    assert got_count == count
