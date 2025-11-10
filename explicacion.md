### ¿Por qué falla la validación de transacciones?

La validación falla porque las primeras 20 transacciones que descargamos son **coinbase**. Una transacción coinbase:

- **Crea** nuevas monedas (subsidio del bloque) y **no gasta** ningún UTXO previo.
- Señala esto usando un **marcador nulo** en su única entrada:
  - `prev_tx = 00...00` (32 bytes en cero)
  - `prev_index = 0xffffffff`

Nuestro verificador (`Tx.verify()`) asume que todas las entradas referencian un UTXO previo “normal”, por lo que intenta:

1. Calcular la **fee** sumando los valores de las entradas (`TxIn.value()`).
2. Para eso, hace `fetch_tx(prev_tx)`; en coinbase, `prev_tx` es `00...00`, que **no es un txid real** sino un **placeholder** definido por el protocolo para indicar “no hay outpoint”.

El nodo/servicio remoto responde:

``` py
0000000000000000000000000000000000000000000000000000000000000000 not found
```

Esa respuesta **no es hex válida**, y el parser (que espera bytes hexadecimales de una transacción real) falla al intentar convertirla, produciendo un error del tipo:

``` bash
ValueError: non-hexadecimal number found in fromhex() ... / unexpected response: ... not found

```


**Conclusión.** No es un bug de nuestra implementación de bloques: es el comportamiento esperado al intentar validar coinbase con un verificador pensado para entradas estándar (P2PKH/P2PK). La coinbase **no tiene UTXO previo** y debe tratarse como un caso especial; de lo contrario, el intento de “buscar su entrada previa” fallará.
