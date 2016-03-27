#!/usr/bin/env python3.5
import argparse
import os
import shlex
import stat
import subprocess


def output_on_failure(cmd, cwd):
    print('cd {} && {}'.format(cwd, cmd))
    ret = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd,
    )
    if ret.returncode:
        raise AssertionError('Command {!r} returned {}!\nOutput:\n{}'.format(
            cmd, ret.returncode, ret.stdout,
        ))


def run_test(bin_path, test):
    print('*' * 79)
    print('{} -c {}'.format(shlex.quote(bin_path), shlex.quote(test)))
    subprocess.check_call((bin_path, '-c', test))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('python')
    parser.add_argument('--needs-lib', action='store_true', default=False)
    args = parser.parse_args()

    assert os.path.exists(args.python), args.python
    os.makedirs('bin', exist_ok=True)

    output_on_failure('./configure', cwd=args.python)
    output_on_failure('make', cwd=args.python)

    bin_path = os.path.join('bin', args.python.replace('-', ''))
    python_abspath = os.path.abspath(os.path.join(args.python, 'python'))

    if args.needs_lib:
        lib_abspath = os.path.abspath(os.path.join(args.python, 'Lib'))
        with open(bin_path, 'w') as exe:
            exe.write(
                '#!/usr/bin/env bash\n'
                "export PYTHONPATH='{}'\n"
                "exec '{}' \"$@\"\n".format(lib_abspath, python_abspath)
            )
        original_mode = os.stat(bin_path).st_mode
        os.chmod(
            bin_path,
            original_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
        )
    else:
        os.symlink(python_abspath, bin_path)

    run_test(bin_path, 'print("hello world!")')
    run_test(bin_path, 'import os; print(os.path.join("foo", "bar"))')


if __name__ == '__main__':
    exit(main())
