"""Backend regression: simplify symbolic X before evaluating defined concrete instances."""

import argparse
import logging
from pathlib import Path

from pyk.kore.rpc import KoreClient, kore_server
from pyk.kore.syntax import App, DV, EVar, SortApp, String


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('definition_dir', type=Path)
    parser.add_argument('--backend-command', default='kore-rpc')
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    int_sort = SortApp('SortInt')
    def token(value):
        return DV(int_sort, String(str(value)))
    variable = EVar('VarX', int_sort)
    expression = App("Lbl'Unds'modInt'Unds'", args=(
        App("Lbl'Unds-LT--LT-'Int'Unds'", args=(variable, token(3))), token(3)))
    def instantiate(term, value):
        return term.bottom_up(lambda item: token(value) if item == variable else item)
    with kore_server(args.definition_dir, 'KWASM-LEMMAS', command=args.backend_command) as server:
        with KoreClient('localhost', server.port, timeout=30) as client:
            def simplify(term):
                result, _ = client.simplify(term)
                return result

            symbolic = simplify(expression)
            print('SYMBOLIC_INPUT', expression.text, flush=True)
            print('SYMBOLIC_RESULT', symbolic.text, flush=True)
            if args.baseline:
                assert symbolic == token(0), symbolic
                assert simplify(instantiate(symbolic, 1)) == token(0)
                assert simplify(instantiate(expression, 1)) == token(2)
                print('BASELINE_CONFIRMED: symbolic collapse=0; defined X=1 input=2', flush=True)
            else:
                assert symbolic != token(0), symbolic
                for value, expected in [(0, 0), (1, 2)]:
                    concrete = instantiate(symbolic, value)
                    actual = simplify(concrete)
                    print(f'PATCHED_INSTANCE: X={value}; result={actual.text}; expected={expected}', flush=True)
                    assert actual == token(expected), actual
                print('PATCHED_REGRESSION_PASS', flush=True)


if __name__ == '__main__':
    main()
