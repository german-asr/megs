import os
import click

from tqdm import tqdm

import audiomate
from audiomate.corpus import subset


SEED = 3294
MAX_DEV_TEST_DURATION = 15000
MAX_TRAIN_UTT_DURATION = 25.0


@click.command()
@click.argument('download_folder', type=click.Path(exists=True))
@click.argument('output_folder', type=click.Path())
def run(download_folder, output_folder):
    corpora_names = [
        ('common_voice', 'common-voice'),
        ('mailabs', 'mailabs'),
        ('swc', 'swc'),
        ('tuda', 'tuda'),
        ('voxforge', 'voxforge'),
    ]

    print('Load corpora')
    corpora = {}

    for name, reader_type in corpora_names:
        print(' - {} ...'.format(name))
        full_path = os.path.join(download_folder, name)
        c = audiomate.Corpus.load(
            full_path,
            reader=reader_type
        )
        corpora[name] = c

    print('Create Train/Dev/Test - if not already exist')
    for name, corpus in corpora.items():
        prepare_corpus(corpus, name)

    print('Insert full subviews')
    #
    #   Insert subviews containing all utterances
    #   so we have a reference when merged
    #
    for name, corpus in corpora.items():
        all_utts = set(corpus.utterances.keys())
        full_filter = subset.MatchingUtteranceIdxFilter(all_utts)
        full_subview = subset.Subview(corpus, filter_criteria=[full_filter])
        corpus.import_subview('full', full_subview)

    print('Suffix subviews')
    #
    #   Suffix subviews to have the correct names when merging
    #
    for name, corpus in corpora.items():
        print(' - {} ...'.format(name))
        original_subview_names = list(corpus.subviews.keys())

        for subview_name in original_subview_names:
            new_subview_name = '{}_{}'.format(subview_name, name)
            corpus.subviews[new_subview_name] = corpus.subviews[subview_name]
            del corpus.subviews[subview_name]

    print('Merge corpora ...')
    full_corpus = audiomate.Corpus.merge_corpora(list(corpora.values()))

    print('Create merged train/test/dev subviews ...')
    for part in ['train', 'dev', 'test']:
        utt_ids = set()

        for name, corpus in corpora.items():
            sv = full_corpus.subviews['{}_{}'.format(part, name)]
            utt_ids.update(sv.utterances.keys())

        part_filter = subset.MatchingUtteranceIdxFilter(utt_ids)
        part_subview = subset.Subview(corpus, filter_criteria=[part_filter])
        full_corpus.import_subview(part, part_subview)

    print('Save ...')
    os.makedirs(output_folder)
    full_corpus.save_at(output_folder)


def prepare_corpus(corpus, name):
    if name != 'common_voice':
        print(' - {}: Find utterances that are too long'.format(name))
        too_long = utts_too_long(corpus)
    else:
        too_long = set()

    if name == 'mailabs':
        # we only use mailabs for training
        # since we don't know the speakers
        train_utts = set(corpus.utterances.keys())
        train_utts = train_utts - too_long
        dev_utts = set()
        test_utts = set()

    elif name == 'tuda':
        # we only use kinect-raw files
        # otherwise sentence of the tuda would occur multiple times
        # in contrast to other datasets
        train_utts = set(corpus.subviews['train_kinect-raw'].utterances.keys())
        train_utts = train_utts - too_long
        dev_utts = set(corpus.subviews['dev_kinect-raw'].utterances.keys())
        test_utts = set(corpus.subviews['test_kinect-raw'].utterances.keys())

    elif name == 'common_voice':
        train_utts = set(corpus.subviews['train'].utterances.keys())
        train_utts = train_utts - too_long
        dev_utts = set(corpus.subviews['dev'].utterances.keys())
        test_utts = set(corpus.subviews['test'].utterances.keys())

    else:
        dur_filter = subset.MatchingUtteranceIdxFilter(too_long, inverse=True)
        dur_subview = subset.Subview(corpus, filter_criteria=[dur_filter])
        train, dev, test = create_train_dev_test(dur_subview)

        train_utts = set(train.utterances.keys())
        dev_utts = set(dev.utterances.keys())
        test_utts = set(test.utterances.keys())

    # Remove all subviews
    for subname in list(corpus.subviews.keys()):
        del corpus.subviews[subname]

    # Add new subviews
    train_filter = subset.MatchingUtteranceIdxFilter(train_utts)
    train_subview = subset.Subview(corpus, filter_criteria=[train_filter])
    corpus.import_subview('train', train_subview)

    dev_filter = subset.MatchingUtteranceIdxFilter(dev_utts)
    dev_subview = subset.Subview(corpus, filter_criteria=[dev_filter])
    corpus.import_subview('dev', dev_subview)

    test_filter = subset.MatchingUtteranceIdxFilter(test_utts)
    test_subview = subset.Subview(corpus, filter_criteria=[test_filter])
    corpus.import_subview('test', test_subview)


def utts_too_long(corpus):
    utts = set()

    for utt in tqdm(corpus.utterances.values()):
        if utt.duration > MAX_TRAIN_UTT_DURATION:
            utts.add(utt.idx)

    return utts


def create_train_dev_test(corpus):
    """
    Create train/dev/test subsets of the given corpus.
    Size is computed using length of the transcriptions.
    """

    total_duration = corpus.total_duration
    test_dev_train_ratio = MAX_DEV_TEST_DURATION / total_duration

    if test_dev_train_ratio > 0.15:
        test_dev_train_ratio = 0.15

    splitter = subset.Splitter(corpus, SEED)
    subviews = splitter.split_by_label_length(
        proportions={
            'train': 1.0 - (2 * test_dev_train_ratio),
            'dev': test_dev_train_ratio,
            'test': test_dev_train_ratio,
        },
        label_list_idx=audiomate.corpus.LL_WORD_TRANSCRIPT,
        separate_issuers=True
    )

    return subviews['train'], subviews['dev'], subviews['test']


if __name__ == '__main__':
    run()
