import sys
from typing import Callable
from typing import TypeVar
from typing import no_type_check


# Python 3.10 or higher
if sys.version_info >= (3, 10):
    from typing import ParamSpec

    Type = type
else:
    from typing_extensions import ParamSpec
    from typing import Type

PS = ParamSpec("PS")
RT = TypeVar("RT")


# pyright: reportUnnecessaryIsInstance=false
# pyright: reportAttributeAccessIssue=false


class deprecated:
    """
    backport of warnings.deprecated decorator from Python 3.13
    Doesn't work on coroutines to simplify the implementation.
    """

    def __init__(
        self,
        message: str,
        /,
        *,
        category: "Type[Warning] | None" = DeprecationWarning,
        stacklevel: int = 1,
    ) -> None:
        if not isinstance(message, str):
            raise TypeError(
                f"Expected an object of type str for 'message', not {type(message).__name__!r}"
            )
        self.message = message
        self.category = category
        self.stacklevel = stacklevel

    def __call__(self, arg: Callable[PS, RT], /) -> Callable[PS, RT]:
        from warnings import warn

        # Make sure the inner functions created below don't
        # retain a reference to self.
        msg = self.message
        category = self.category
        stacklevel = self.stacklevel
        if category is None:
            arg.__deprecated__ = msg  # type: ignore
            return arg
        elif isinstance(arg, type):
            import functools
            from types import MethodType

            original_new = arg.__new__

            @no_type_check
            @functools.wraps(original_new)
            def __new__(cls, /, *args, **kwargs):
                if cls is arg:
                    warn(msg, category=category, stacklevel=stacklevel + 1)
                if original_new is not object.__new__:
                    return original_new(cls, *args, **kwargs)
                # Mirrors a similar check in object.__new__.
                elif cls.__init__ is object.__init__ and (args or kwargs):
                    raise TypeError(f"{cls.__name__}() takes no arguments")
                else:
                    return original_new(cls)

            arg.__new__ = staticmethod(__new__)  # type: ignore

            original_init_subclass = arg.__init_subclass__
            # We need slightly different behavior if __init_subclass__
            # is a bound method (likely if it was implemented in Python)
            if isinstance(original_init_subclass, MethodType):
                original_init_subclass = original_init_subclass.__func__

                @no_type_check
                @functools.wraps(original_init_subclass)
                def __init_subclass__(*args, **kwargs):
                    warn(msg, category=category, stacklevel=stacklevel + 1)
                    return original_init_subclass(*args, **kwargs)

                arg.__init_subclass__ = classmethod(__init_subclass__)  # type: ignore
            # Or otherwise, which likely means it's a builtin such as
            # object's implementation of __init_subclass__.
            else:

                @no_type_check
                @functools.wraps(original_init_subclass)
                def __init_subclass__(*args, **kwargs):
                    warn(msg, category=category, stacklevel=stacklevel + 1)
                    return original_init_subclass(*args, **kwargs)

                arg.__init_subclass__ = __init_subclass__  # type: ignore[method-assign]

            arg.__deprecated__ = __new__.__deprecated__ = msg  # type: ignore
            __init_subclass__.__deprecated__ = (  # pyrefly: ignore[missing-attribute]
                msg
            )
            return arg  # pyrefly: ignore[bad-return]
        elif callable(arg):
            import functools

            @functools.wraps(arg)
            def wrapper(*args: PS.args, **kwargs: PS.kwargs) -> RT:
                warn(
                    msg, category=category, stacklevel=stacklevel + 1
                )  # pyrefly: ignore[no-matching-overload]
                return arg(*args, **kwargs)

            arg.__deprecated__ = wrapper.__deprecated__ = msg  # type: ignore
            return wrapper
        else:
            raise TypeError(
                "@deprecated decorator with non-None category must be applied to "
                f"a class or callable, not {arg!r}"
            )
