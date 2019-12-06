import spoteno

import audiomate
from audiomate.corpus.validation import base


class TextNormalizationValidator(base.Validator):
    """
    Checks if the transcript can be normalized with spoteno.
    """

    def __init__(self):
        self.normalizer = spoteno.Normalizer.de()

    def name(self):
        return 'Normalization-Validator'

    def validate(self, corpus):
        """
        Perform the validation on the given corpus.

        Args:
            corpus (Corpus): The corpus to test/validate.

        Returns:
            InvalidItemsResult: Validation result.
        """
        utt_ids = []
        transcripts = []
        ll_idx = audiomate.corpus.LL_WORD_TRANSCRIPT

        for utt in corpus.utterances.values():
            transcript = utt.label_lists[ll_idx].join()
            transcripts.append(transcript)
            utt_ids.append(utt.idx)

        result = self.normalizer.debug_list(transcripts)

        invalid_utterances = {}

        for i, (output, invalid_characters) in enumerate(result):
            utt_idx = utt_ids[i]
            transcript = transcripts[i]
            if len(invalid_characters) > 0 or len(output) <= 0:
                invalid_utterances[utt_idx] = (
                    transcript, list(invalid_characters)
                )

        passed = len(invalid_utterances) <= 0

        return base.InvalidItemsResult(
            passed,
            invalid_utterances,
            name=self.name(),
            info={}
        )
