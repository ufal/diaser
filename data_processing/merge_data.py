import argparse
import json
import os
import glob
import zipfile
import tempfile


def _write_zip(output_file, data):
    outfile = os.path.abspath(output_file)
    base_outfile = os.path.basename(output_file)
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        write_json(base_outfile, data)
        with zipfile.ZipFile(outfile + '.zip', 'w', zipfile.ZIP_DEFLATED) as ozfd:
            ozfd.write(base_outfile)


def _write_json(output_file, data):
    with open(output_file, 'wt') as ofd:
        json.dump(data, ofd, indent=2, sort_keys=True)


def write_json(output_file, data, compress=False):
    if compress:
        _write_zip(output_file, data)
    else:
        _write_json(output_file, data)


def read_json(input_file, compressed=False):
    if compressed:
        with zipfile.ZipFile(input_file, 'r') as zfd:
            name = '.'.join(input_file.split('.')[:-1])
            with zfd.open(os.path.basename(name), 'r') as fd:
                data = json.load(fd)
    else:
        with open(input_file, 'rt') as fd:
            data = json.load(fd)
    return data


def main(args):
    data = []
    for name in glob.glob(os.path.join(args.data_dir, '*.json')):
        data.extend(read_json(name))
    for name in glob.glob(os.path.join(args.data_dir, '*.zip')):
        data.extend(read_json(name, compressed=True))
    write_json(args.output_file, data, compress=args.compress)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir')
    parser.add_argument('--output_file')
    parser.add_argument('--compress', action='store_true')
    args = parser.parse_args()
    main(args)
