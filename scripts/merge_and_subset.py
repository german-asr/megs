import os
import click

import audiomate
from audiomate.corpus import subset


SEED = 3294


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
            reader=reader_type,
        )
        corpora[name] = c

    print('Create Train/Dev/Test - if not already exist')
    # tuda/common-voice already have predefined train/test/dev sets
    # mailabs is not used as dev/test, since the speakers are not known
    # so we would have split the corpus very coarse
    for name in ['swc', 'voxforge']:
        print(' - {} ...'.format(name))
        c = corpora[name]
        train, dev, test = create_train_dev_test(c)
        c.import_subview('train', train)
        c.import_subview('dev', dev)
        c.import_subview('test', test)

    print('Remove/Rename subviews')
    # common voice
    del corpora['common_voice'].subviews['other']
    del corpora['common_voice'].subviews['validated']

    # mailabs
    del corpora['mailabs'].subviews['de_DE']

    # tuda
    # we only use kinect-raw files
    # otherwise sentence of the tuda would occur multiple times
    # in contrast to other datasets
    tuda = corpora['tuda']

    del tuda.subviews['train']
    del tuda.subviews['dev']
    del tuda.subviews['test']

    tuda.subviews['train'] = tuda.subviews['train_kinect-raw']
    tuda.subviews['dev'] = tuda.subviews['dev_kinect-raw']
    tuda.subviews['test'] = tuda.subviews['test_kinect-raw']

    for mic in ['yamaha', 'kinect-beam', 'kinect-raw', 'realtek', 'samson']:
        del tuda.subviews[mic]

        for part in ['dev', 'test', 'train']:
            del tuda.subviews['{}_{}'.format(part, mic)]

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
        for name in ['common_voice', 'tuda', 'voxforge', 'swc']:
            sv = full_corpus.subviews['{}_{}'.format(part, name)]
            utt_ids.update(sv.utterances.keys())

        if part == 'train':
            utt_ids.update(
                full_corpus.subviews['full_mailabs'].utterances.keys())

        part_filter = subset.MatchingUtteranceIdxFilter(utt_ids)
        part_subview = subset.Subview(corpus, filter_criteria=[part_filter])
        full_corpus.import_subview(part, part_subview)

    print('Save ...')
    os.makedirs(output_folder)
    full_corpus.save_at(output_folder)


def create_train_dev_test(corpus):
    """
    Create train/dev/test subsets of the given corpus.
    Size is computed using length of the transcriptions.
    """
    splitter = subset.Splitter(corpus, SEED)
    subviews = splitter.split_by_label_length(
        proportions={
            'train': 0.7,
            'dev': 0.15,
            'test': 0.15,
        },
        label_list_idx=audiomate.corpus.LL_WORD_TRANSCRIPT,
        separate_issuers=True
    )

    return subviews['train'], subviews['dev'], subviews['test']


if __name__ == '__main__':
    run()
