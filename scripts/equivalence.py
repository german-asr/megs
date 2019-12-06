import os
import hashlib
import click
import json

import audiomate
from tqdm import tqdm


SEED = 3294


@click.group()
def cli():
    pass


@cli.command()
@click.argument('data_folder', type=click.Path(exists=True))
def generate(data_folder):
    full_path = os.path.join(data_folder, 'full')
    state_path = os.path.join(data_folder, 'state.json')

    state = generate_state(full_path)

    with open(state_path, 'w') as f:
        json.dump(state, f)


@cli.command()
@click.argument('data_folder', type=click.Path(exists=True))
def check(data_folder):
    full_path = os.path.join(data_folder, 'full')
    state_path = os.path.join(data_folder, 'state.json')

    with open(state_path, 'r') as f:
        state = json.load(f)

    actual_state = generate_state(full_path)

    if compare(state, actual_state):
        print('OK - Your data matches the state of the repository')
    else:
        print('NOT OK - Your data differs from the state of the repository')


def generate_state(path):
    state = {
        'meta_files': {},
    }

    print('Hash meta files')
    for filename in os.listdir(path):
        if filename.endswith('txt') or filename.endswith('json'):
            print(' - {} ...'.format(filename))
            file_path = os.path.join(path, filename)

            if filename == 'issuers.json':
                hash_value = hash_issuers_json(file_path)
            else:
                hash_value = hash_file(file_path)

            state['meta_files'][filename] = hash_value

    print('Hash audio files')
    corpus = audiomate.Corpus.load(path)
    tracks = sorted(corpus.tracks.values(), key=lambda x: x.idx)

    # We only hash file-size
    # Otherwise it would take to long
    h = hashlib.new('md5')

    for track in tqdm(tracks, total=corpus.num_tracks):
        stat = os.stat(track.path)
        size = stat.st_size
        h.update(size.to_bytes(4, byteorder='big'))

    hash_value = h.hexdigest()
    state['audio_files'] = hash_value

    return state


def hash_file(path):
    with open(path, 'rb') as f:
        content = f.read()

    h = hashlib.new('md5')
    h.update(content)
    return h.hexdigest()


def hash_issuers_json(path):
    with open(path, 'r') as f:
        content = json.load(f)

    h = hashlib.new('md5')

    for x, y in sorted(content.items(), key=lambda x: x[0]):
        parts = [x]
        for k, v in sorted(y.items(), key=lambda x: x[0]):
            parts.append(k)
            parts.append(v)

    h.update(' '.join(parts).encode('utf-8'))
    return h.hexdigest()


def compare(reference, actual):
    ok = True

    for meta_file, hash_value in reference['meta_files'].items():
        if hash_value != actual['meta_files'][meta_file]:
            print('Hash value of {} differs'.format(meta_file))
            ok = False

    if reference['audio_files'] != actual['audio_files']:
        print('Hash value of audio files differs')
        ok = False

    return ok


if __name__ == '__main__':
    cli()
