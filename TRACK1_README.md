# Track 1: Fix and Extend

## The situation

You inherited `taskboard.py`, a small in-memory task tracker. The team has a test
suite, and right now **a number of tests are failing**. Your manager also wants two
new features added.

## Your tasks

### Part 1: Fix the failing tests
Run the tests from this folder:

```
python -m unittest -v
```

Find out why tests fail and fix the code. The **spec is written at the top of
`taskboard.py`**. When the code and the spec disagree, the spec wins.

Do not edit the test file to make tests pass. The tests are correct.

### Part 2: Implement two features
Two methods currently raise `NotImplementedError`. Their docstrings describe what
they should do:

- `tasks_by_tag(tag)`
- `summary(today=None)`

### Part 3 (stretch, if you finish early)
- Add at least two tests of your own for edge cases you think the suite misses.
- Write a short note on any design weaknesses you noticed in `taskboard.py`.

## Done means

- All tests pass (`OK` at the bottom of the output).
- You can explain, in your own words, **what was wrong in each place you made a
  fix** and why your fix is right.

## Reminders

- No packages to install. Standard library only.
- Save your prompt log as you go.
- When AI suggests a fix, ask yourself: does it match the *spec*, or does it just
  make the test go green?
