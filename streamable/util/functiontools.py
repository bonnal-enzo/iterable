from typing import Any, Callable, Coroutine, Generic, Tuple, Type, TypeVar, overload

T = TypeVar("T")
R = TypeVar("R")


class ErrorMappedFunc(Generic[T, R]):
    def __init__(
        self, func: Callable[[T], R], source: Type[Exception], target: Type[Exception]
    ) -> None:
        self.func = func
        self.source = source
        self.target = target

    def __call__(self, arg: T) -> R:
        try:
            return self.func(arg)
        except self.source as e:
            raise self.target() from e


def reraise_as(
    func: Callable[[T], R], source: Type[Exception], target: Type[Exception]
) -> Callable[[T], R]:
    return ErrorMappedFunc(func, source, target)


class SidifiedFunc(Generic[T]):
    def __init__(self, func: Callable[[T], Any]) -> None:
        self.func = func

    def __call__(self, arg: T) -> T:
        self.func(arg)
        return arg


def sidify(func: Callable[[T], Any]) -> Callable[[T], T]:
    return SidifiedFunc(func)


def async_sidify(
    func: Callable[[T], Coroutine]
) -> Callable[[T], Coroutine[Any, Any, T]]:
    async def wrap(arg: T) -> T:
        coroutine = func(arg)
        if not isinstance(coroutine, Coroutine):
            raise TypeError(
                f"The function is expected to be an async function, i.e. it must be a function returning a Coroutine object, but returned a {type(coroutine)}."
            )
        await coroutine
        return arg

    return wrap


class TupledFunc(Generic[R]):
    def __init__(self, func: Callable[..., R]) -> None:
        self.func = func

    def __call__(self, args: Tuple) -> R:
        return self.func(*args)


T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")


@overload
def star(func: Callable[[T], R]) -> Callable[[Tuple], R]:
    return TupledFunc(func)


@overload
def star(func: Callable[[T1, T2], R]) -> Callable[[Tuple[T1, T2]], R]:
    return TupledFunc(func)


@overload
def star(func: Callable[[T1, T2, T3], R]) -> Callable[[Tuple[T1, T2, T3]], R]:
    return TupledFunc(func)


@overload
def star(func: Callable[[T1, T2, T3, T4], R]) -> Callable[[Tuple[T1, T2, T3, T4]], R]:
    return TupledFunc(func)


@overload
def star(func: Callable[..., R]) -> Callable[[Tuple], R]:
    return TupledFunc(func)


def star(func: Callable[..., R]) -> Callable[[Tuple], R]:
    return TupledFunc(func)
