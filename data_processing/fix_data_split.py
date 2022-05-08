import argparse
import glob
import json
import os
import tempfile
import zipfile

def _write_zip(output_file, data):
    old_cwd = os.getcwd()
    outfile = os.path.abspath(output_file)
    base_outfile = os.path.basename(output_file)
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        write_json(base_outfile, data)
        with zipfile.ZipFile(outfile + '.zip', 'w', zipfile.ZIP_DEFLATED) as ozfd:
            ozfd.write(base_outfile)
    os.chdir(old_cwd)


def _write_json(output_file, data):
    with open(output_file, 'wt') as ofd:
        json.dump(data, ofd, indent=2, sort_keys=True)


def write_json(output_file, data, compress=False):
    if compress:
        _write_zip(output_file, data)
    else:
        _write_json(output_file, data)


def main(args):
    full_data = []

    for fp in glob.glob(os.path.join(args.input_dir, '*.zip')):
        with zipfile.ZipFile(fp, 'r') as zfd:
            name = '.'.join(fp.split('.')[:-1])
            with zfd.open(os.path.basename(name), 'r') as fd:
                data = json.load(fd)
            # fix missing split for Multiwoz data
            for x in data:
                if x['split'] is None:
                    x['split'] = fp.split('/')[-1].split('.')[0]
            full_data.extend(data)

    train_data, dev_data, test_data = [], [], []

    # Split traindev into train & dev & eventually to test
    with open(args.train_split_ids) as f:
        train_ids = f.read().splitlines()
    with open(args.dev_split_ids) as f:
        dev_ids = f.read().splitlines()

    for x in full_data:
        if x['split'] == 'train':
            train_data.append(x)
        elif x['split'] == 'dev':
            dev_data.append(x)
        elif x['split'] == 'test':
            test_data.append(x)
        else:  # special for train-dev camrest
            if x['dialogue_id'] in train_ids:
                train_data.append(x)
            elif x['dialogue_id'] in dev_ids:
                dev_data.append(x)
            else:
                test_data.append(x)

    os.makedirs(args.output_dir, exist_ok=True)
    for data, split in zip([train_data, dev_data, test_data], ['train', 'dev', 'test']):
        write_json(
            os.path.join(args.output_dir, f'{split}.json'),
            data,
            args.compress
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir')
    parser.add_argument('--output-dir')
    parser.add_argument('--compress', action='store_true')
    parser.add_argument('--train-split-ids', type=str)
    parser.add_argument('--dev-split-ids', type=str)
    args = parser.parse_args()
    main(args)
