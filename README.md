# `kioss`
**Keep I/O Simple and Stupid**

[![Actions Status](https://github.com/bonnal-enzo/kioss/workflows/test/badge.svg)](https://github.com/bonnal-enzo/kioss/actions) [![Actions Status](https://github.com/bonnal-enzo/kioss/workflows/PyPI/badge.svg)](https://github.com/bonnal-enzo/kioss/actions)

Expressive pythonic library that has been designed to ***ease the development of (reverse) ETL data pipelines***, with features such as *multithreading*, *rate limiting*, *batching*, and *exceptions handling*.

## 1. Install

```bash
pip install kioss
```

## 2. Import
```python
from kioss import Pipe
```

## 3. Init

```python
integers: Pipe[int] = Pipe(source=lambda: range(10))
```

Instantiate a `Pipe` by providing a function returning an `Iterable` (the data source).

## 4. Declare operations

A `Pipe` is ***immutable***, meaning that applying an operation returns a new child pipe while the parent pipe remains unchanged.

There are 2 kinds of operations:
- **transformations**: to act on the pipe's elements
- **controls**: to configure the behaviors of the iteration over the pipe


```python
odd_squares: Pipe[int] = (
    integers
    .map(lambda x: x ** 2) # transformation
    .filter(lambda x: x % 2 == 1) # transformation
    .slow(freq=10) # control
)
```
All operations are described in the ***Operations guide*** section.

## 5. Iterate

Once your pipe's declaration is done you can iterate over it. Our `Pipe[int]` being an `Iterable[int]`, you are free to iterate over it the way you want, e.g.:
```python
set(rate_limited_odd_squares)
```
```python
sum(rate_limited_odd_squares)
```
```python
for i in rate_limited_odd_squares:
    ...
```

Alternatively, a pipe also exposes a convenient method `.run` to launch an iteration over itself until exhaustion. It catches exceptions occurring during iteration and optionnaly collects output elements into a list to return. At the end it raises if exceptions occurred.

```python
odd_squares: List[int] = rate_limited_odd_squares.run(collect_limit=1024)

assert odd_squares == [1, 9, 25, 49, 81]
```



---

# ***Operations guide***

Let's keep the same example:
```python
integers = Pipe(lambda: range(10))
```

# A. Transformations
![](./img/transform.gif)

## `.map`
Defines the application of a function on parent elements.
```python
integer_strings: Pipe[str] = integers.map(str)
```

You can pass an optional `n_threads` argument to `.map` for a concurrent application of the function using multiple threads.

## `.do`
Defines the application of a function on parent elements like `.map`, but the parent elements will be forwarded instead of the result of the function.

```python
printed_integers: Pipe[int] = integers.do(print)
```

It also accepts a `n_threads` parameter.

## `.filter`
Defines the filtering of parent elements based on a predicate function.

```python
pair_integers: Pipe[int] = integers.filter(lambda x: x % 2 == 0)
```

## `.batch`

Defines the grouping of parent elements into batches.

```python
integer_batches: Pipe[List[int]] = integers.batch(size=100, period=60)
```

In this example a batch will be a list of 100 elements.

It may contain less elements in the following cases:
- the pipe is exhausted
- an exception occurred
- more than 60 seconds (`period` argument) has elapsed since the last batch has been yielded.

## `.flatten`

Defines the ungrouping of parent elements assuming that the parent elements are `Iterable`s.

```python
integers: Pipe[int] = integer_batches.flatten()
```

It also accepts a `n_threads` parameter to flatten concurrently several parent iterables.

## `.chain`

Defines the concatenation of the parent pipe with other pipes. The resulting pipe yields the elements of one pipe until it is exhausted and then moves to the next one. It starts with the pipe on which `.chain` is called.

```python
one_to_ten_integers: Pipe[int] = Pipe(lambda: range(1, 11))
eleven_to_twenty_integers: Pipe[int] = Pipe(lambda: range(11, 21))
twenty_one_to_thirty_integers: Pipe[int] = Pipe(lambda: range(21, 31))

one_to_thirty_integers: Pipe[int] = one_to_ten_integers.chain(
    eleven_to_twenty_integers,
    twenty_one_to_thirty_integers,
)
```

# B. Controls
![](./img/control.gif)

## `.slow`

Defines a maximum rate at which parent elements will be yielded.

```python
slowed_integers: Pipe[int] = integers.slow(freq=2)
```

The rate is expressed in elements per second, here a maximum of 2 elements per second will be yielded when iterating on the pipe.

## `.observe`

Defines that the iteration process will be logged.

```python
observed_slowed_integers: Pipe[int] = slowed_integers.observe(what="integers from 0 to 9")
```

When iterating over the pipe, you should get an output like:

```
INFO - iteration over 'integers from 0 to 9' will be logged.
INFO - 1 integers from 0 to 9 have been yielded, in elapsed time 0:00:00.000283, with 0 error produced
INFO - 2 integers from 0 to 9 have been yielded, in elapsed time 0:00:00.501373, with 0 error produced
INFO - 4 integers from 0 to 9 have been yielded, in elapsed time 0:00:01.501346, with 0 error produced
INFO - 8 integers from 0 to 9 have been yielded, in elapsed time 0:00:03.500864, with 0 error produced
INFO - 10 integers from 0 to 9 have been yielded, in elapsed time 0:00:04.500547, with 0 error produced
```

As you can notice the logs can never be overwhelming because they are produced logarithmically.


## `.catch`

Defines that the provided type of exception will be catched.

```python
inverse_floats: Pipe[float] = integers.map(lambda x: 1/x)
safe_inverse_floats: Pipe[float] = inverse_floats.catch(ZeroDivisionError)
```

You can additionnally provide a `when` argument: a function that takes the parent element as input and decides whether or not to catch the exception.


---
---


*If you want more inspiration on how to leverage kioss, feel free to check the `./examples` folder.*
