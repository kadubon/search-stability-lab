# Results Interpretation

## Supported most clearly

- `H2` is the clearest current story.
- Across Layer A and the bundled Layer B slice, `C3 > C0` is the most stable controller-law contrast.
- Layer A also supports compression-alias harm as a real mechanism in the simulator.

## Partially supported

- `H1` has partial support in Layer A because higher budgets improved pooled success, but the pattern is not uniformly monotone by controller.
- `H4` has partial support in Layer A because longer lag increased alias rates for the compression-heavy controller.
- Layer B provides directional support for substitution-first control, but only on bundled mechanistic probe tasks.
- Layer B now also provides directional reset-probe support because `C4` and `C5` both beat `C0` on the bundled reset suite.
- Layer B compression probes now provide limited outcome-sensitive support because `C5` resolved the bundled compression tasks while `C0` and `C1` did not.

## Unsupported or still unclear

- Layer B does not currently support a strong reset-dominance story between `C4` and `C5`.
- Layer B compression evidence is still too small-scale to be treated as strong validation.
- Broad external-validity claims remain unsupported.

## `C5` interpretation

`C5` is mixed and should not be overclaimed.

- In Layer A, it is useful but not uniformly dominant.
- In Layer B on Gemini, it is mixed.
- In the new reset probe, it improves on `C0` but does not separate from `C4`.
- In the new compression probe, it improves on `C0` and `C1`, but only on two bundled tasks.
- In Layer B on the local CPU block, it is further confounded by repeated structured-output failures.

## Local structured-output confound

The local CPU runs recorded repeated malformed structured-output failures.

That means:

- the harness still executed and logged outcomes
- but some outcomes are confounded by output-format fragility
- those runs should not be presented as clean evidence about controller quality alone
- the new bounded repair layer did not materially reduce final invalidity in the completed probe runs

## Reading hierarchy

1. Layer A exact simulator results
2. Layer B bundled task-outcome and proxy results
3. local CPU malformed-output diagnostics
