from malaya_speech.supervised import separation
from herpetologist import check_type

_availability = {
    'fastsep-2': {
        'Size (MB)': 78.7,
        'Quantized Size (MB)': 20.5,
        'SISNR PIT': 14.156882,
    },
    'fastsep-4': {
        'Size (MB)': 155,
        'Quantized Size (MB)': 40.2,
        'SISNR PIT': 19.6825,
    },
}

_availability_mel = {
    'fastsep-2': {'Size (MB)': 97.8, 'MAE PIT': 0},
    'fastsep-4': {'Size (MB)': 97.8, 'MAE PIT': 0},
}


def available_deep_wav():
    """
    List available FastSep models trained on raw 8k wav.
    """
    from malaya_speech.utils import describe_availability

    return describe_availability(_availability, text = 'Tested on 1k samples')


def available_deep_mel():
    """
    List available FastSep models trained on Melspectrogram 22k wav.
    """
    from malaya_speech.utils import describe_availability

    return describe_availability(
        _availability_mel, text = 'Tested on 1k samples'
    )


@check_type
def deep_wav(model: str = 'fastsep-4', quantized: bool = False, **kwargs):
    """
    Load FastSep model, trained on raw 8k wav using SISNR PIT loss.

    Parameters
    ----------
    model : str, optional (default='fastsep-4')
        Model architecture supported. Allowed values:

        * ``'fastsep-4'`` - FastSep 4 layers trained on raw 8k wav.
        * ``'fastsep-2'`` - FastSep 2 layers trained on raw 8k wav.
    quantized : bool, optional (default=False)
        if True, will load 8-bit quantized model. 
        Quantized model not necessary faster, totally depends on the machine.

    Returns
    -------
    result : malaya_speech.model.tf.Split class
    """

    model = model.lower()
    if model not in _availability:
        raise Exception(
            'model not supported, please check supported models from `malaya_speech.multispeaker_separation.available_deep_wav()`.'
        )
    return separation.load(
        model = model,
        module = 'multispeaker-separation-wav',
        quantized = quantized,
        **kwargs
    )


@check_type
def deep_mel(model: str = 'fastsep-4', quantized: bool = False, **kwargs):
    """
    Load FastSep model, trained on Melspectrogram 22k wav using MAE PIT loss.

    Parameters
    ----------
    model : str, optional (default='fastsep-4')
        Model architecture supported. Allowed values:

        * ``'fastsep-4'`` - FastSep 4 layers trained on Melspectrogram 22k wav.
        * ``'fastsep-6'`` - FastSep 6 layers trained on Melspectrogram 22k wav.
    quantized : bool, optional (default=False)
        if True, will load 8-bit quantized model. 
        Quantized model not necessary faster, totally depends on the machine.

    Returns
    -------
    result : malaya_speech.model.tf.Split class
    """

    model = model.lower()
    if model not in _availability_mel:
        raise Exception(
            'model not supported, please check supported models from `malaya_speech.multispeaker_separation.available_deep_mel()`.'
        )
    return separation.load(
        model = model,
        module = 'multispeaker-separation-mel',
        quantized = quantized,
        **kwargs
    )
