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


if __name__ == '__main__':
    for b in main():
        print(b)
