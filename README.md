# d1000

A fast, powerful, and extensible dice engine for virtual tabletops! This is a fork of the [d20 Python library](https://github.com/zhudotexe/d20) to be used with [the Lenny D&D bot](https://github.com/DaFrankort/lenny-dnd-bot).

## Key Features

- Quick to start - just use `d10.roll()`!
- Optimized for speed and memory efficiency
- Highly extensible API for custom behaviour and dice stringification
- Built-in execution limits against malicious dice expressions
- Tree-based dice representation for easy traversal

## Installing

**Requires Python 3.11+**.

```bash
pip install git+https://github.com/pipieter/d100@main
```

## Quickstart

```pycon
>>> import d100
>>> result = d100.roll("1d20+5")
>>> str(result)
'1d20 (10) + 5 = `15`'
>>> result.total
15
>>> result.crit
<CritType.NORMAL: 0>
>>> str(result.ast)
'1d20 + 5'
```

An interactive session can be started by calling the library as a module.

```pycon
python3 -m 100

>>> roll 1d20
'1d20 (6) = 6'

>>> distribution 1d4
Calculation time: 0.00 seconds
Mean:  2.50
Stdev: 1.12

1.  25.000%  ██████████████████████████████████████████████████
2.  25.000%  ██████████████████████████████████████████████████
3.  25.000%  ██████████████████████████████████████████████████
4.  25.000%  ██████████████████████████████████████████████████
```

# Rolls

## Documentation

Check out the docs on [Read the Docs](https://d20.readthedocs.io/en/latest/start.html)!

### Generating typings

The typings of the file can be generated with the following commands, which also ensure consistent formatting in the typings:

```bash
# mypy is required for stubgen
pip install mypy
stubgen -p d100 --include-docstrings -o typings
black typings
isort typings
```

## Dice Syntax

This is the grammar supported by the dice parser, roughly ordered in how tightly the grammar binds.

### Numbers

These are the atoms used at the base of the syntax tree.

| Name    | Syntax                           | Description           | Examples                       |
| ------- | -------------------------------- | --------------------- | ------------------------------ |
| literal | `INT`, `DECIMAL`                 | A literal number.     | `1`, `0.5`, `3.14`             |
| dice    | `INT? "d" (INT \| "%")`          | A set of die.         | `d20`, `3d6`                   |
| set     | `"(" (num ("," num)* ","?)? ")"` | A set of expressions. | `()`, `(2,)`, `(1, 3+3, 1d20)` |

Note that `(3d6)` is equivalent to `3d6`, but `(3d6,)` is the set containing the one element `3d6`.

### Set Operations

These operations can be performed on dice and sets.

#### Grammar

| Name     | Syntax               | Description                        | Examples        |
| -------- | -------------------- | ---------------------------------- | --------------- |
| set_op   | `operation selector` | An operation on a set (see below). | `kh3`, `ro<3`   |
| selector | `seltype INT`        | A selection on a set (see below).  | `3`, `h1`, `>2` |

#### Operators

Most operators are always followed by a selector, and operate on the items in the set that match the selector.

| Syntax | Name                | Description                                                                              |
| ------ | ------------------- | ---------------------------------------------------------------------------------------- |
| k      | keep                | Keeps all matched values.                                                                |
| p      | drop                | Drops all matched values.                                                                |
| rr     | reroll              | Rerolls all matched values until none match. (Dice only)                                 |
| ro     | reroll once         | Rerolls all matched values once. (Dice only)                                             |
| ra     | reroll and add      | Rerolls up to one matched value once, keeping the original roll. (Dice only)             |
| rs     | reroll and subtract | Reroll and subtract up to one matched value once, keeping the original roll. (Dice only) |
| e      | explode on          | Rolls another die for each matched value. (Dice only)                                    |
| mi     | minimum             | Sets the minimum value of each die. (Dice only)                                          |
| ma     | maximum             | Sets the maximum value of each die. (Dice only)                                          |

Some operators are shorthands for other operators. These don't require selectors.

| Syntax | Name         | Description                                                   |
| ------ | ------------ | ------------------------------------------------------------- |
| red    | RED critical | Equivalent to rs1raN where N is the maximum value of the dice |

#### Advantage

Two operators are supported to re-roll expressions and take specific results. These are `advantage` and `disadvantage`.

| Syntax | Name         | Description                                          |
| ------ | ------------ | ---------------------------------------------------- |
| adv    | advantage    | Roll an expression twice and take the higher result. |
| dis    | disadvantage | Roll an expression twice and take the lower result.  |

An expression can only have one of these, and that operator can only be used. For example, `4d6advkh3` is a valid expression, but `4d6advdis` is not.

#### Selectors

Selectors select from the remaining kept values in a set.

| Syntax | Name           | Description                                           |
| ------ | -------------- | ----------------------------------------------------- |
| X      | literal        | All values in this set that are literally this value. |
| hX     | highest X      | The highest X values in the set.                      |
| lX     | lowest X       | The lowest X values in the set.                       |
| \>X    | greater than X | All values in this set greater than X.                |
| <X     | less than X    | All values in this set less than X.                   |

### Unary Operations

| Syntax | Name     | Description              |
| ------ | -------- | ------------------------ |
| +X     | positive | Does nothing.            |
| -X     | negative | The negative value of X. |

### Binary Operations

| Syntax | Name           |
| ------ | -------------- |
| X \* Y | multiplication |
| X / Y  | division       |
| X // Y | int division   |
| X % Y  | modulo         |
| X + Y  | addition       |
| X - Y  | subtraction    |
| X == Y | equality       |
| X >= Y | greater/equal  |
| X <= Y | less/equal     |
| X > Y  | greater than   |
| X < Y  | less than      |
| X != Y | inequality     |

### Examples

```pycon
>>> from d100 import roll
>>> r = roll("4d6kh3")  # highest 3 of 4 6-sided dice
>>> r.total
14
>>> str(r)
'4d6kh3 (4, 4, **6**, ~~3~~) = `14`'

>>> r = roll("2d6ro<3")  # roll 2d6s, then reroll any 1s or 2s once
>>> r.total
9
>>> str(r)
'2d6ro<3 (**~~1~~**, 3, **6**) = `9`'

>>> r = roll("8d6mi2")  # roll 8d6s, with each die having a minimum roll of 2
>>> r.total
33
>>> str(r)
'8d6mi2 (1 -> 2, **6**, 4, 2, **6**, 2, 5, **6**) = `33`'

>>> r = roll("(1d4 + 1, 3, 2d6kl1)kh1")  # the highest of 1d4+1, 3, and the lower of 2 d6s
>>> r.total
3
>>> str(r)
'(1d4 (2) + 1, ~~3~~, ~~2d6kl1 (2, 5)~~)kh1 = `3`'
```

## Custom Stringifier

By default, d100 stringifies the result of each dice roll formatted in Markdown, which may not be useful in your
application.
To change this behaviour, you can create a subclass
of [`d100.Stringifier`](https://github.com/pipieter/d100/blob/master/d100/roll/stringifiers.py)
(or `d100.SimpleStringifier` as a starting point), and implement the `_str_*` methods to customize how your dice tree is
stringified.

Then, simply pass an instance of your stringifier into the `roll()` function!

```pycon
>>> import d100
>>> class MyStringifier(d100.SimpleStringifier):
...     def _stringify(self, node):
...         if not node.kept:
...             return 'X'
...         return super()._stringify(node)
...
...     def _str_expression(self, node):
...         return f"The result of the roll {self._stringify(node.roll)} was {int(node.total)}"

>>> result = d100.roll("4d6e6kh3", stringifier=MyStringifier())
>>> str(result)
'The result of the roll 4d6e6kh3 (X, 5, 6!, 6!, X, X) was 17'
```

## Traversing Dice Results

The raw results of dice rolls are returned in [`Expression`](https://github.com/avrae/d20/blob/master/d20/models.py#L76)
objects, which can be accessed as such:

```pycon
>>> from d100 import roll
>>> result = roll("3d6 + 1d4 + 3")
>>> str(result)
'3d6 (4, **6**, **6**) + 1d4 (**1**) + 3 = `20`'
>>> result.expr
<Expression roll=<BinOp left=<BinOp left=<Dice num=3 size=6 values=[<Die size=6 values=[<Literal 4>]>, <Die size=6 values=[<Literal 6>]>, <Die size=6 values=[<Literal 6>]>] operations=[]> op=+ right=<Dice num=1 size=4 values=[<Die size=4 values=[<Literal 1>]>] operations=[]>> op=+ right=<Literal 3>>>
```

or, in a easier-to-read format,

```text
<Expression
    roll=<BinOp
        left=<BinOp
            left=<Dice
                num=3
                size=6
                values=[
                    <Die size=6 values=[<Literal 4>]>,
                    <Die size=6 values=[<Literal 6>]>,
                    <Die size=6 values=[<Literal 6>]>
                ]
                operations=[]
            >
            op=+
            right=<Dice
                num=1
                size=4
                values=[
                    <Die size=4 values=[<Literal 1>]>
                ]
                operations=[]
            >
        >
        op=+
        right=<Literal 3>
    >
>
```

From here, `Expression.children` returns a tree of nodes representing the expression from left to right, each of which
may have children of their own. This can be used to easily search for specific dice, look for the left-most operand,
or modify the result by adding in resistances or other modifications.

### Examples

Finding the left and right-most operands:

```pycon
>>> from d100 import roll

>>> binop = roll("1 + 2 + 3 + 4")
>>> left = binop.expr
>>> while left.children:
...     left = left.children[0]
>>> left
<Literal 1>

>>> right = binop.expr
>>> while right.children:
...     right = right.children[-1]
>>> right
<Literal 4>

>>> from d100 import utils  # these patterns are available in the utils submodule:
>>> utils.leftmost(binop.expr)
<Literal 1>
>>> utils.rightmost(binop.expr)
<Literal 4>
```

Searching for the d4:

```pycon
>>> from d100 import roll, Dice, SimpleStringifier, utils

>>> mixed = roll("-1d8 + 4 - (3, 1d4)kh1")
>>> str(mixed)
'-1d8 (**8**) + 4 - (3, ~~1d4 (3)~~)kh1 = `-7`'
>>> root = mixed.expr
>>> result = utils.dfs(root, lambda node: isinstance(node, Dice) and node.num == 1 and node.size == 4)
>>> result
<Dice num=1 size=4 values=[<Die size=4 values=[<Literal 3>]>] operations=[]>
>>> SimpleStringifier().stringify(result)
'1d4 (3)'
```

As a note, even though a `Dice` object is the parent of `Die` objects, `Dice.children` returns an empty list, since it's
more common to look for the dice, and not each individual component of that dice.

## Performance

By default, the parser caches the 256 most frequently used dice expressions in an LFU cache, allowing for a significant speedup when rolling many of the same kinds of rolls.

With caching:

```bash
$ python3 -m timeit -s "from d100 import roll" "roll('1d20')"
10000 loops, best of 5: 21.6 usec per loop
$ python3 -m timeit -s "from d100 import roll" "roll('100d20')"
500 loops, best of 5: 572 usec per loop
$ python3 -m timeit -s "from d100 import roll; expr='1d20+'*50+'1d20'" "roll(expr)"
500 loops, best of 5: 732 usec per loop
$ python3 -m timeit -s "from d100 import roll" "roll('10d20rr<20')"
1000 loops, best of 5: 1.13 msec per loop
```

Without caching:

```bash
$ python3 -m timeit -s "from d100 import roll" "roll('1d20')"
5000 loops, best of 5: 61.6 usec per loop
$ python3 -m timeit -s "from d100 import roll" "roll('100d20')"
500 loops, best of 5: 620 usec per loop
$ python3 -m timeit -s "from d100 import roll; expr='1d20+'*50+'1d20'" "roll(expr)"
500 loops, best of 5: 2.1 msec per loop
$ python3 -m timeit -s "from d100 import roll" "roll('10d20rr<20')"
1000 loops, best of 5: 1.26 msec per loop
```

# Distributions

Aside from rolling dice, d100 can also be used to calculate the distribution of dice following the exact same syntax.

A distribution can be created using the `distribution` function. This returns an object with all the possible values. Each value is a possible dice result. All values have an equal chance of appearing, and a value can appear multiple times.

The possible values can be found with `.keys()`. Individual values can be retrieved with `.get()`. The mean and standard deviation can be found with `.mean()` and `.stdev()` respectively.

```python
from d100 import distribution

dist = distribution("1d8 + 4")
print(dist.get(5)) # 0.125
print(dist.mean()) # 8.50
```

## Performance

Internally, two distribution builders are used depending on the modifiers used. These two distributions use convolutions and discrete keys, respectively. The convolution builder is significantly faster (up to 100x performance for certain expressions), but is also more limited. Depending on which builder is used, performance may change drastically.

More specifically, the discrete key builder is used in the following cases:

- The e and ra modifiers are used.
- The h and l selectors are used for any modifier.

Care should thus be taken in these scenarios, as the execution time can exponentially increase with the number of dice and the number of sides the dice have. This library does not utilize any internal limits, and it is up to the user to avoid overly complex expressions.
