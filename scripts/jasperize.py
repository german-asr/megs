import os
import click

import audiomate
from audiomate.corpus import io


@click.command()
@click.argument('in_folder', type=click.Path(exists=True))
@click.argument('out_folder', type=click.Path())
@click.option('--base-folder', default=None, type=click.Path())
def run(in_folder, out_folder, base_folder):
    if not os.path.exists(out_folder):
        if base_folder is None:
            base_folder = os.path.dirname(out_folder)

        w = io.NvidiaJasperWriter(
            num_workers=8,
            no_check=True,
            data_base_path=base_folder
        )
        target_audio_path = os.path.join(out_folder, 'audio')
        os.makedirs(target_audio_path)

        print('Load source corpus')
        ds = audiomate.Corpus.load(in_folder)
        print('Save jasper corpus')
        w.save(ds, out_folder)
    else:
        print('Already jasperized')


if __name__ == '__main__':
    run()
