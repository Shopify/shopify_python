# pylint:disable=missing-docstring,unused-import
import typing


def one_param(seq):
    # type: (typing.Sequence[str]) -> str    # [sequence-of-string]
    copy = seq  # type:typing.Sequence[str]  # [sequence-of-string]
    return copy[0]


def multiple_params(message, seq, index):
    # type: (string, typing.Sequence[str], int) -> str  # [sequence-of-string]
    return message + seq[index]


def return_type(message_1, message_2):
    # type: (str, str) -> typing.Sequence[str]  # [sequence-of-string]
    return [message_1, message_2]
