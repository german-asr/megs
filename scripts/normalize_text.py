import os
import click

import audiomate
from audiomate import annotations
import spoteno


@click.command()
@click.argument('full_folder', type=click.Path())
@click.argument('out_folder', type=click.Path())
def run(full_folder, out_folder):
    if not os.path.exists(out_folder):
        print('Load source corpus')
        ds = audiomate.Corpus.load(full_folder)

        print('Normalize transcripts')
        normalizer = spoteno.Normalizer.de()
        utt_ids = []
        transcripts = []
        ll_idx = audiomate.corpus.LL_WORD_TRANSCRIPT

        for utt in ds.utterances.values():
            transcript = utt.label_lists[ll_idx].join()
            transcripts.append(transcript)
            utt_ids.append(utt.idx)

        result = normalizer.normalize_list(transcripts)

        for i, utt_idx in enumerate(utt_ids):
            orig = transcripts[i]
            normalized = result[i]

            ll_orig = annotations.LabelList.create_single(
                orig,
                'word-transcript-orig'
            )

            ll_normalized = annotations.LabelList.create_single(
                normalized,
                audiomate.corpus.LL_WORD_TRANSCRIPT
            )

            ds.utterances[utt_idx].set_label_list(ll_orig)
            ds.utterances[utt_idx].set_label_list(ll_normalized)

        print('Save normalized corpus')
        os.makedirs(out_folder, exist_ok=True)
        ds.save_at(out_folder)
    else:
        print('Already normalized')


if __name__ == '__main__':
    run()
