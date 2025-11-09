from io import BytesIO
from block import Block, FullBlock, TESTNET_GENESIS_BLOCK

# 1) Parsear el header génesis (usa Block porque TESTNET_GENESIS_BLOCK es solo header)
hdr = Block.parse(BytesIO(TESTNET_GENESIS_BLOCK))
print('Header OK, version:', hdr.version)

# 2) Construir un FullBlock "a mano" con el mismo header (nr_trans=0 solo para probar serialize/hash/pow)
fb = FullBlock(
    version=hdr.version,
    prev_block=hdr.prev_block,
    merkle_root=hdr.merkle_root,
    timestamp=hdr.timestamp,
    bits=hdr.bits,
    nonce=hdr.nonce,
    nr_trans=0,
    txs=[]
)

# 3) Verificar que serialize() sea de 80 bytes y que hash/pow funcionen
ser = fb.serialize()
print('Header length:', len(ser))           # debe ser 80
print('Block hash  :', fb.hash().hex())     # hash del header
print('check_pow   :', fb.check_pow())      # True para el génesis
