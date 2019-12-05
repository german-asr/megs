import os
import click
import json

import audiomate
from audiomate.corpus import validation

import validators


@click.command()
@click.argument('download_folder', type=click.Path(exists=True))
@click.argument('output_folder', type=click.Path())
def run(download_folder, output_folder):
    corpora_names = [
        ('voxforge', 'voxforge'),
        ('common_voice', 'common-voice'),
        ('mailabs', 'mailabs'),
        ('swc', 'swc'),
        ('tuda', 'tuda'),
    ]

    for name, reader_type in corpora_names:
        print('Run validation for {}'.format(name))
        full_path = os.path.join(download_folder, name)
        out_path = os.path.join(output_folder, name)
        c = audiomate.Corpus.load(
            full_path,
            reader=reader_type,
            include_invalid_items=True
        )

        run_validation(c, out_path)
        print('-'*40)


def run_validation(corpus, output_path):
    os.makedirs(output_path, exist_ok=True)

    all_invalid = set()

    utts = find_invalid_audio_tracks(output_path, corpus)
    all_invalid.update(utts)

    utts = find_invalid_character_ratios(output_path, corpus)
    all_invalid.update(utts)

    utts = find_invalid_transcripts(output_path, corpus)
    all_invalid.update(utts)

    all_report_path = os.path.join(output_path, 'invalid_all.json')
    write_report(all_report_path, sorted(all_invalid))


def find_invalid_audio_tracks(output_path, corpus):
    #
    # Find invalid audio tracks
    #

    report_path = os.path.join(output_path, 'invalid_tracks.json')

    if not os.path.isfile(report_path):
        print('Validate tracks ...')
        v = validation.TrackReadValidator(num_workers=4)
        result = v.validate(corpus)
        invalid_tracks = result.invalid_items
        write_report(report_path, invalid_tracks)
    else:
        invalid_tracks = read_report(report_path)
        print('Validate tracks - Already done')

    invalid_utts = []

    for utt in corpus.utterances.values():
        if utt.track in invalid_tracks:
            invalid_utts.append(utt.idx)

    return invalid_utts


def find_invalid_character_ratios(output_path, corpus):
    #
    # Find invalid chracter ratios
    #
    report_path = os.path.join(output_path, 'invalid_character_ratio.json')

    if not os.path.isfile(report_path):
        print('Validate character ratio ...')
        v = validation.UtteranceTranscriptionRatioValidator(
            max_characters_per_second=25,
            label_list_idx=audiomate.corpus.LL_WORD_TRANSCRIPT,
            num_threads=4
        )
        result = v.validate(corpus)
        invalid_utts = result.invalid_items
        write_report(report_path, invalid_utts)
    else:
        invalid_utts = read_report(report_path)
        print('Validate character ratio - Already done')

    return invalid_utts.keys()


def find_invalid_transcripts(output_path, corpus):
    #
    # Find transcripts that can't be normalized
    #
    report_path = os.path.join(output_path, 'invalid_transcripts.json')

    if not os.path.isfile(report_path):
        print('Validate transcript normalization ...')
        v = validators.TextNormalizationValidator()
        result = v.validate(corpus)
        invalid_utts = result.invalid_items
        write_report(report_path, invalid_utts)
    else:
        invalid_utts = read_report(report_path)
        print('Validate transcript normalization - Already done')

    return invalid_utts.keys()


def write_report(path, report):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False)


def read_report(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    run()
