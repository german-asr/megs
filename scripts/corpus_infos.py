import os
import click

import audiomate
from audiomate.utils import jsonfile


@click.group()
def cli():
    pass


@cli.command()
@click.argument('download_folder', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
def downloaded(download_folder, output_path):
    corpora_names = [
        ('common_voice', 'common-voice'),
        ('mailabs', 'mailabs'),
        ('swc', 'swc'),
        ('tuda', 'tuda'),
        ('voxforge', 'voxforge'),
    ]

    infos = {}

    if os.path.isfile(output_path):
        print('Info file already there')
        return

    for name, reader_type in corpora_names:
        full_path = os.path.join(download_folder, name)
        cinfo = get_corpus_info(name, full_path, reader_type)
        infos[name] = cinfo

    jsonfile.write_json_to_file(output_path, infos)


@cli.command()
@click.argument('full_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
def full(full_path, output_path):
    if os.path.isfile(output_path):
        print('Info file already there')
        return

    cinfo = get_corpus_info('full', full_path, 'default')
    jsonfile.write_json_to_file(output_path, cinfo)


def get_corpus_info(name, full_path, reader_type):
    print('Get infos for {}'.format(name))
    c = audiomate.Corpus.load(
        full_path,
        reader=reader_type,
    )

    cinfo = {
        'duration': c.total_duration,
        'num_utterances': c.num_utterances,
        'num_issuers': c.num_issuers,
        'subviews': {},
    }

    for sname, subview in c.subviews.items():
        sinfo = {
            'duration': subview.total_duration,
            'num_utterances': subview.num_utterances,
            'num_issuers': subview.num_issuers
        }
        cinfo['subviews'][sname] = sinfo

    return cinfo


if __name__ == '__main__':
    cli()
