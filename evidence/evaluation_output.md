# Reproducible Evaluation Output

Commands run from the project root:

```text
python -m pytest -q
python -m src.evaluate
```

Output:

```text
......                                                                   [100%]
6 passed in 0.46s

TuneMatch reliability evaluation
[PASS] exact pop match: first=Sunrise City; confidence=1.00; notes=0
[PASS] exact lofi match: first=Midnight Coding; confidence=1.00; notes=0
[PASS] exact jazz match: first=Coffee Shop Stories; confidence=1.00; notes=0
[PASS] catalog gap warning: first=Midnight Coding; confidence=0.15; notes=2

Summary: 4/4 checks passed.
```

The exact elapsed time for the test suite will vary by machine. The expected result is six passing tests and four passing evaluation checks.
