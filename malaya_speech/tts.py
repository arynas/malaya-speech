from malaya_speech.path import (
    PATH_TTS_TACOTRON2,
    S3_PATH_TTS_TACOTRON2,
    PATH_TTS_FASTSPEECH2,
    S3_PATH_TTS_FASTSPEECH2,
    PATH_TTS_FASTPITCH,
    S3_PATH_TTS_FASTPITCH,
)
from malaya_speech.utils.text import (
    convert_to_ascii,
    collapse_whitespace,
    put_spacing_num,
    tts_encode,
)
from malaya_speech.supervised import tts
import numpy as np
import re

_tacotron2_availability = {
    'male': {
        'Size (MB)': 104,
        'Quantized Size (MB)': 26.3,
        'Combined loss': 0.1838,
    },
    'female': {
        'Size (MB)': 104,
        'Quantized Size (MB)': 26.3,
        'Combined loss': 0.1887,
    },
    'husein': {
        'Size (MB)': 104,
        'Quantized Size (MB)': 26.3,
        'Combined loss': 0.1165,
    },
    'haqkiem': {
        'Size (MB)': 104,
        'Quantized Size (MB)': 26.3,
        'Combined loss': 0.1375,
    },
    'female-singlish': {
        'Size (MB)': 104,
        'Quantized Size (MB)': 26.3,
        'Combined loss': 0.0923,
    },
}
_fastspeech2_availability = {
    'male': {
        'Size (MB)': 125,
        'Quantized Size (MB)': 31.7,
        'Combined loss': 1.8,
    },
    'female': {
        'Size (MB)': 125,
        'Quantized Size (MB)': 31.7,
        'Combined loss': 1.932,
    },
    'husein': {
        'Size (MB)': 125,
        'Quantized Size (MB)': 31.7,
        'Combined loss': 0.5832,
    },
    'haqkiem': {
        'Size (MB)': 125,
        'Quantized Size (MB)': 31.7,
        'Combined loss': 0.5663,
    },
    'female-singlish': {
        'Size (MB)': 125,
        'Quantized Size (MB)': 31.7,
        'Combined loss': 0.5112,
    },
}

_fastpitch_availability = {
    'male': {
        'Size (MB)': 123,
        'Quantized Size (MB)': 31.1,
        'Combined loss': 1.614,
    },
    'female': {
        'Size (MB)': 123,
        'Quantized Size (MB)': 31.1,
        'Combined loss': 1.669,
    },
    'husein': {
        'Size (MB)': 123,
        'Quantized Size (MB)': 31.1,
        'Combined loss': 0.52515,
    },
    'haqkiem': {
        'Size (MB)': 123,
        'Quantized Size (MB)': 31.1,
        'Combined loss': 0.5186,
    },
    'female-singlish': {
        'Size (MB)': 123,
        'Quantized Size (MB)': 31.1,
        'Combined loss': 0.4083,
    },
}

_pad = 'pad'
_start = 'start'
_eos = 'eos'
_punctuation = "!'(),.:;? "
_special = '-'
_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
_rejected = '\'():;"'
_punct = ':;,.?'


MALAYA_SPEECH_SYMBOLS = (
    [_pad, _start, _eos] + list(_special) + list(_punctuation) + list(_letters)
)


class TextIDS:
    def __init__(
        self,
        normalizer,
        pad_to,
        sentence_tokenizer,
        true_case,
        understand_punct=True,
    ):
        self.normalizer = normalizer
        self.pad_to = pad_to
        self.sentence_tokenizer = sentence_tokenizer
        self.true_case = true_case
        self.understand_punct = understand_punct

    def normalize(
        self,
        string,
        normalize=True,
        assume_newline_fullstop=False,
        **kwargs
    ):
        string = convert_to_ascii(string)
        if assume_newline_fullstop:
            string = string.replace('\n', '. ')
            string = self.sentence_tokenizer(string, minimum_length=0)
            string = '. '.join(string)

        if self.true_case:
            string = self.true_case.predict([string], beam_search=False)[0]

        string = re.sub(r'[ ]+', ' ', string).strip()
        if string[-1] in '-,':
            string = string[:-1]
        if string[-1] not in '.,?!':
            string = string + '.'

        string = string.replace('&', ' dan ')
        string = string.replace(':', ',').replace(';', ',')
        if normalize:
            t = self.normalizer._tokenizer(string)
            for i in range(len(t)):
                if t[i] == '-':
                    t[i] = ','
            string = ' '.join(t)
            string = self.normalizer.normalize(
                string,
                check_english=False,
                normalize_entity=False,
                normalize_text=False,
                normalize_url=True,
                normalize_email=True,
                normalize_telephone=True,
            )
            string = string['normalize']
        else:
            string = string
        string = put_spacing_num(string)
        string = ''.join(
            [
                c
                for c in string
                if c in MALAYA_SPEECH_SYMBOLS and c not in _rejected
            ]
        )
        if not self.understand_punct:
            string = ''.join([c for c in string if c not in _punct])
        string = re.sub(r'[ ]+', ' ', string).strip()
        string = string.lower()
        ids = tts_encode(string, MALAYA_SPEECH_SYMBOLS, add_eos=False)
        ids = ids + [2, 0, 0, 0]
        text_input = np.array(ids)
        num_pad = self.pad_to - ((len(text_input) + 2) % self.pad_to)
        text_input = np.pad(
            text_input, ((1, 1)), 'constant', constant_values=((1, 2))
        )
        text_input = np.pad(
            text_input, ((0, num_pad)), 'constant', constant_values=0
        )

        return string, text_input


def load_text_ids(
    pad_to: int = 8,
    true_case=None,
    quantized=False,
    understand_punct=True,
    **kwargs
):
    try:
        import malaya
    except BaseException:
        raise ModuleNotFoundError(
            'malaya not installed. Please install it by `pip install malaya` and try again.'
        )

    normalizer = malaya.normalize.normalizer(date=False, time=False)
    sentence_tokenizer = malaya.text.function.split_into_sentences
    if true_case:
        true_case = malaya.true_case.transformer(
            model=true_case, quantized=quantized, **kwargs
        )

    return TextIDS(
        normalizer=normalizer,
        pad_to=pad_to,
        sentence_tokenizer=sentence_tokenizer,
        true_case=true_case,
        understand_punct=understand_punct,
    )


def available_tacotron2():
    """
    List available Tacotron2, Text to Mel models.
    """
    from malaya_speech.utils import describe_availability

    return describe_availability(
        _tacotron2_availability,
        text='`husein`, `haqkiem` and `female-singlish` combined loss from training set',
    )


def available_fastspeech2():
    """
    List available FastSpeech2, Text to Mel models.
    """
    from malaya_speech.utils import describe_availability

    return describe_availability(
        _fastspeech2_availability,
        text='`husein`, `haqkiem` and `female-singlish` combined loss from training set',
    )


def available_fastpitch():
    """
    List available FastPitch, Text to Mel models.
    """
    from malaya_speech.utils import describe_availability

    return describe_availability(
        _fastpitch_availability,
        text='`husein`, `haqkiem` and `female-singlish` combined loss from training set',
    )


def tacotron2(
    model: str = 'male',
    quantized: bool = False,
    pad_to: int = 8,
    true_case: str = None,
    **kwargs
):
    """
    Load Tacotron2 TTS model.

    Parameters
    ----------
    model : str, optional (default='male')
        Model architecture supported. Allowed values:

        * ``'female'`` - Tacotron2 trained on female voice.
        * ``'male'`` - Tacotron2 trained on male voice.
        * ``'husein'`` - Tacotron2 trained on Husein voice, https://www.linkedin.com/in/husein-zolkepli/
        * ``'haqkiem'`` - Tacotron2 trained on Haqkiem voice, https://www.linkedin.com/in/haqkiem-daim/
        * ``'female-singlish'`` - Tacotron2 trained on female Singlish voice, https://www.imda.gov.sg/programme-listing/digital-services-lab/national-speech-corpus

    quantized : bool, optional (default=False)
        if True, will load 8-bit quantized model.
        Quantized model not necessary faster, totally depends on the machine.

    pad_to : int, optional (default=8)
        size of pad character with 0. Increase can stable up prediction on short sentence, we trained on 8.

    true_case: str, optional (default=None)
        Load True Case model from https://malaya.readthedocs.io/en/latest/load-true-case.html,
        to fix case sensitive and punctuation errors. Allowed values:

        * ``'small'`` - Small size True Case model.
        * ``'base'`` - Base size True Case model.
        * ``None`` - no True Case model.

    Returns
    -------
    result : malaya_speech.model.tf.Tacotron class
    """
    model = model.lower()

    if model not in _tacotron2_availability:
        raise ValueError(
            'model not supported, please check supported models from `malaya_speech.tts.available_tacotron2()`.'
        )

    text_ids = load_text_ids(
        pad_to=pad_to,
        true_case=true_case,
        quantized=quantized,
        **kwargs
    )

    return tts.tacotron_load(
        path=PATH_TTS_TACOTRON2,
        s3_path=S3_PATH_TTS_TACOTRON2,
        model=model,
        name='text-to-speech',
        normalizer=text_ids,
        quantized=quantized,
        **kwargs
    )


def fastspeech2(
    model: str = 'male',
    quantized: bool = False,
    pad_to: int = 8,
    true_case: str = None,
    **kwargs
):
    """
    Load Fastspeech2 TTS model.

    Parameters
    ----------
    model : str, optional (default='male')
        Model architecture supported. Allowed values:

        * ``'female'`` - Fastspeech2 trained on female voice.
        * ``'male'`` - Fastspeech2 trained on male voice.
        * ``'husein'`` - Fastspeech2 trained on Husein voice, https://www.linkedin.com/in/husein-zolkepli/
        * ``'haqkiem'`` - Fastspeech2 trained on Haqkiem voice, https://www.linkedin.com/in/haqkiem-daim/
        * ``'female-singlish'`` - Fastspeech2 trained on female Singlish voice, https://www.imda.gov.sg/programme-listing/digital-services-lab/national-speech-corpus

    quantized : bool, optional (default=False)
        if True, will load 8-bit quantized model.
        Quantized model not necessary faster, totally depends on the machine.

    pad_to : int, optional (default=8)
        size of pad character with 0. Increase can stable up prediction on short sentence, we trained on 8.

    true_case: str, optional (default=None)
        Load True Case model from https://malaya.readthedocs.io/en/latest/load-true-case.html,
        to fix case sensitive and punctuation errors. Allowed values:

        * ``'small'`` - Small size True Case model.
        * ``'base'`` - Base size True Case model.
        * ``None`` - no True Case model.

    Returns
    -------
    result : malaya_speech.model.tf.Fastspeech class
    """

    model = model.lower()

    if model not in _fastspeech2_availability:
        raise ValueError(
            'model not supported, please check supported models from `malaya_speech.tts.available_fastspeech2()`.'
        )

    text_ids = load_text_ids(
        pad_to=pad_to,
        true_case=true_case,
        quantized=quantized,
        **kwargs
    )
    return tts.fastspeech_load(
        path=PATH_TTS_FASTSPEECH2,
        s3_path=S3_PATH_TTS_FASTSPEECH2,
        model=model,
        name='text-to-speech',
        normalizer=text_ids,
        quantized=quantized,
        **kwargs
    )


def fastpitch(
    model: str = 'male',
    quantized: bool = False,
    pad_to: int = 8,
    true_case: str = None,
    **kwargs
):
    """
    Load Fastspitch TTS model.

    Parameters
    ----------
    model : str, optional (default='male')
        Model architecture supported. Allowed values:

        * ``'female'`` - Fastpitch trained on female voice.
        * ``'male'`` - Fastpitch trained on male voice.
        * ``'husein'`` - Fastpitch trained on Husein voice, https://www.linkedin.com/in/husein-zolkepli/
        * ``'haqkiem'`` - Fastpitch trained on Haqkiem voice, https://www.linkedin.com/in/haqkiem-daim/
        * ``'female-singlish'`` - Fastpitch trained on female Singlish voice, https://www.imda.gov.sg/programme-listing/digital-services-lab/national-speech-corpus

    quantized : bool, optional (default=False)
        if True, will load 8-bit quantized model.
        Quantized model not necessary faster, totally depends on the machine.

    pad_to : int, optional (default=8)
        size of pad character with 0. Increase can stable up prediction on short sentence, we trained on 8.

    true_case: str, optional (default=None)
        Load True Case model from https://malaya.readthedocs.io/en/latest/load-true-case.html,
        to fix case sensitive and punctuation errors. Allowed values:

        * ``'small'`` - Small size True Case model.
        * ``'base'`` - Base size True Case model.
        * ``None`` - no True Case model.

    Returns
    -------
    result : malaya_speech.model.tf.Fastpitch class
    """

    model = model.lower()

    if model not in _fastpitch_availability:
        raise ValueError(
            'model not supported, please check supported models from `malaya_speech.tts.available_fastpitch()`.'
        )

    text_ids = load_text_ids(
        pad_to=pad_to,
        true_case=true_case,
        quantized=quantized,
        **kwargs
    )
    return tts.fastpitch_load(
        path=PATH_TTS_FASTPITCH,
        s3_path=S3_PATH_TTS_FASTPITCH,
        model=model,
        name='text-to-speech',
        normalizer=text_ids,
        quantized=quantized,
        **kwargs
    )
