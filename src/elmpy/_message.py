"""The type parameter that every generic elmpy class shares.

`Message` stands for "the type of message this value can produce". It is private:
user code defines its own `type Message = ...` union and never imports this one.

It is declared covariant on purpose. With the shorter `class Element[Message]`
syntax, pyright infers "invariant" on Python 3.13+ (because of the `__replace__`
method that frozen dataclasses gained), and then rejects ordinary code such as
returning a `button(...)` stored in a local variable from a view.
Functions and type aliases still use the short PEP 695 syntax.
"""

from typing import TypeVar

Message = TypeVar("Message", covariant=True)
