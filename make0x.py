#!/usr/bin/env python3
import argparse
import os
import shlex
import stat
import subprocess


def output_on_failure(cmd, cwd):
    print(f'$ cd {cwd} && {cmd}')
    ret = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd,
    )
    if ret.returncode:
        raise AssertionError('Command {!r} returned {}!\nOutput:\n{}'.format(
            cmd, ret.returncode, ret.stdout,
        ))


def run_test(bin_path, test):
    print('*' * 79)
    print(f'$ {shlex.quote(bin_path)} /dev/stdin <<< {shlex.quote(test)}')
    subprocess.run((bin_path, '/dev/stdin'), check=True, input=test.encode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('python')
    args = parser.parse_args()

    assert os.path.exists(args.python), args.python
    os.makedirs('bin', exist_ok=True)

    output_on_failure('make', cwd=f'{args.python}/src')

    bin_path = os.path.join('bin', args.python.replace('-', ''))
    python_abspath = os.path.abspath(os.path.join(args.python, 'src/python'))

    lib_abspath = os.path.abspath(os.path.join(args.python, 'lib'))
    with open(bin_path, 'w') as exe:
        exe.write(
            f'#!/usr/bin/env bash\n'
            f"export PYTHONPATH='{lib_abspath}'\n"
            f"exec '{python_abspath}' \"$@\"\n",
        )
    original_mode = os.stat(bin_path).st_mode
    os.chmod(
        bin_path,
        original_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
    )

    run_test(bin_path, 'print(1 + 1)\n')
    run_test(bin_path, "print('hello world!')\n")


if __name__ == '__main__':
    exit(main())
