# pylint:disable=missing-docstring,unused-import
import typing


def one_param(seq: typing.Sequence[str]) -> str:    # [sequence-of-string]
    copy: typing.Sequence[str] = seq    # [sequence-of-string]
    return copy[0]


def multiple_params(
        message: str,
        seq: typing.Sequence[str],      # [sequence-of-string]
        index: int) -> str:
    return message + seq[index]


def return_type(message_1: str, message_2: str) -> typing.Sequence[str]:      # [sequence-of-string]
    return [message_1, message_2]
