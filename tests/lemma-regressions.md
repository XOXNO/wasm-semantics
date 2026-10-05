# Shift/modulus lemma regression

The deleted trusted simplification used the condition `M < 2^N` to conclude
`(X << N) mod M = 0`. That inequality does not establish divisibility.

All operands in the counterexample are defined:

```text
X = 1, N = 3, M = 3
3 < 2^3
(1 << 3) mod 3 = 8 mod 3 = 2
```

The regression simplifies symbolic `X` before substituting a concrete value.
A concrete-only test could evaluate builtin arithmetic first and miss the
incorrect symbolic rewrite.

From the repository root, with K v7.1.337 and kore-rpc 0.1.155 on PATH:

```sh
kompile pykwasm/src/pykwasm/kdist/wasm-semantics/kwasm-lemmas.md \
  --backend haskell \
  --main-module KWASM-LEMMAS \
  --syntax-module WASM-TEXT-SYNTAX \
  --md-selector k \
  --output-definition /tmp/kwasm-modulus-check \
  --warnings-to-errors --emit-json
python tests/shift_mod_lemma_control.py \
  /tmp/kwasm-modulus-check
```

The Python environment needs the existing `kframework`/pyk dependency.
The driver sends Int KORE directly and does not parse compiler JSON metadata.
It starts a local RPC server and makes bounded simplify requests; no proof
graph or admitted claim is used.

For a separately compiled unmodified v0.1.155 definition, pass `--baseline`.
That control requires the old symbolic result to be zero while evaluating the
original expression with X=1 returns two. The patched control checks the
symbolic result is not zero, then evaluates X=0 and X=1 to zero and two.

Independent review compiled both complete KWASM-LEMMAS definitions from isolated
source copies. Both builds and both controls exited zero with the recorded
versions. Only the deleted rule differed between the source copies.
The checked-in driver is byte-identical to the executed driver:
`5507276ce2afe9be66966663347739cbdb46885b3dda520e32cc2ba11cc4983c`.

This removes one confirmed false lemma. It does not validate the remaining
trusted identities. Komet's full optional KWASM-LEMMAS import stays disabled,
and existing contract proof runtimes are unchanged.
