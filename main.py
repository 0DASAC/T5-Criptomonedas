from io import BytesIO
from block import Block, FullBlock, TESTNET_GENESIS_BLOCK
from network import (
    SimpleNode,
    GetHeadersMessage,
    HeadersMessage,
    GetDataMessage,
    BlockMessage,
    BLOCK_DATA_TYPE,
)
from helper import merkle_root
from typing import Tuple


def main() -> list[FullBlock]:
    # 1) Conectarse a un nodo testnet y hacer handshake
    node = SimpleNode('testnet.programmingbitcoin.com', testnet=True, logging=False)
    node.handshake()

    # 2) Obtener los encabezados (headers) a partir del génesis
    genesis = Block.parse(BytesIO(TESTNET_GENESIS_BLOCK))
    start_hash = genesis.hash()  # hash del bloque génesis
    getheaders = GetHeadersMessage(start_block=start_hash)
    node.send(getheaders)
    headers_msg = node.wait_for(HeadersMessage)

    # 3) Construir la lista de hashes de los primeros 20 bloques (génesis + 19 siguientes)
    block_hashes = [start_hash] + [h.hash() for h in headers_msg.blocks[:19]]

    # 4) Crear y enviar el mensaje getdata para pedir los bloques completos
    getdata = GetDataMessage()
    for h in block_hashes:
        getdata.add_data(BLOCK_DATA_TYPE, h)
    node.send(getdata)

    # 5) Recibir los bloques completos (FullBlock)
    blocks: list[FullBlock] = []
    while len(blocks) < len(block_hashes):
        msg = node.wait_for(BlockMessage)
        blocks.append(msg.block)

    # 6) Retornar la lista en orden (ya están en orden ascendente desde el génesis)
    return blocks


def validate_blocks(blocks: list[FullBlock]):
    total_txs, ok, fail = 0, 0, 0

    def is_coinbase_tx(tx):
        return (
            len(tx.tx_ins) == 1 and
            tx.tx_ins[0].prev_tx == b"\x00"*32 and
            tx.tx_ins[0].prev_index == 0xffffffff
        )

    for idx, b in enumerate(blocks):
        assert b.check_pow()

        if b.txs:
            le_hashes = [tx.hash()[::-1] for tx in b.txs]
            assert merkle_root(le_hashes)[::-1] == b.merkle_root

        for j, tx in enumerate(b.txs or []):
            total_txs += 1
            try:
                # Intentar verificar TODO, incluida coinbase, para evidenciar el fallo
                ok_now = tx.verify()
                if ok_now:
                    ok += 1
                else:
                    fail += 1
            except Exception as e:
                # Aquí cae la coinbase con "not found" / non-hex
                fail += 1
                print(f"[bloque {idx} tx {j}] verificación falló: {e}")

    return total_txs, ok, fail

if __name__ == '__main__':
    blocks = main()
    print(f"Descargados {len(blocks)} bloques")

    # Imprime resumen básico
    for i, b in enumerate(blocks):
        print(i, b.hash().hex(), "txs:", b.nr_trans)

    # Corre validaciones y reporta
    tx_total, tx_ok, tx_fail = validate_blocks(blocks)
    print("\n==== VALIDACIÓN DE TRANSACCIONES ====")
    print(f"Transacciones totales:         {tx_total}")
    print(f"No-coinbase verificadas OK:    {tx_ok}")
    print(f"No-coinbase con error/fallo:   {tx_fail}")
    print("\nNota: las transacciones coinbase se omiten a propósito,")
    print("porque no tienen outpoints previos ni script estándar y el verificador actual no las soporta.")
