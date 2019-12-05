import os
import click

import audiomate
from audiomate.corpus import conversion


@click.command()
@click.argument('full_folder', type=click.Path())
@click.argument('out_folder', type=click.Path())
def run(full_folder, out_folder):
    if not os.path.exists(out_folder):
        converter = conversion.WavAudioFileConverter(
            num_workers=8,
            sampling_rate=16000,
            separate_file_per_utterance=True,
            force_conversion=False
        )

        target_audio_path = os.path.join(out_folder, 'audio')
        os.makedirs(target_audio_path)

        print('Load source corpus')
        ds = audiomate.Corpus.load(full_folder)
        print('Convert')
        waverized_ds = converter.convert(ds, target_audio_path)
        print('Save converted corpus')
        waverized_ds.save_at(out_folder)
    else:
        print('Already waverized')


if __name__ == '__main__':
    run()
