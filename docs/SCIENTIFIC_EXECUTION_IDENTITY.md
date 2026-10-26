# Scientific execution and performance identity

## Reaction declarations and execution coefficients

EPDM typed reaction networks, V2 semantic validation and direct canonical
publication share the same stoichiometric identity check. Each execution-matrix
column must contain exactly the coefficients declared by that reaction, in the
declared state order, with zero for every undeclared state. All coefficients must
be finite real numbers. The network owns immutable copies of input sequences.

Matrix shape, a fresh content digest and zero conservation residual are separate
checks. A balanced column doubled from `[-1, 1]` to `[-2, 2]` preserves site
inventory but doubles the activation kinetics. Conservation audits therefore
inspect the actual execution matrix, while identity validation prevents a
different balanced model from being represented as the declared model.

The regression uses only a synthetic activation channel with rate constant
`0.002 1/s` and initial potential-site inventory `2 mol`. The independent solution
is `2 exp(-0.002 t) mol`; the initial derivative is `[-0.004, 0.004] mol/s`.
Software verification leaves scientific and engineering approval unevaluated.

## State-vector positions and species identity

A generated state's `index` is its position in `variables`, `state_ids`, packed
vectors and reaction-matrix rows. Typed construction, V2 semantic validation and
canonical publication enforce this same positional contract. Merely having the
set of indices `0..n-1` is insufficient: permuting variables while retaining their
old indices sends a feed written with `index_of("N_E")` to a different species.
Total inventory can still close while the species result is wrong.

The state definition owns immutable copies of its variable, site-family and
terminal sequences before caching indices. Changing the caller's original lists
cannot alter the published layout or its digest. Custom state ordering remains
supported when each index is updated to the new position and matrix rows use that
same order. The implementation rejects an inconsistent layout instead of silently
reordering an already prepared vector. Existing generated layouts and their
digests remain unchanged.

The regression disables every reaction and feeds only ethylene at `0.2 mol/s`
for `1 s`. The independent species balance is `N_i(t) = N_i(0) + F_i t`, including
unchanged propylene and solvent inventories. It checks both the standard layout
and a consistently reordered custom layout through RHS evaluation and adaptive
integration. Matching digests alone cannot make an inconsistent layout valid.

## Property applicability through the process-package gate

Direct POE property qualification validates the existing packaged
`property_method.schema.json` contract before its physical and applicability
checks. Required ranges, composition domains, selection basis and SI declarations
cannot be replaced by `null` to suppress a gate. Present malformed fields fail;
missing required evidence retains the existing HOLD behavior unless another
contract error independently requires FAIL. Optional `custom_equations` remains
optional for standard methods and is required by the existing CUSTOM-method gate.

A structurally valid record still needs ordered finite physical ranges, usable
benchmarks and valid error metrics. Queries outside a qualified range and
`DECLARED_HOLD` continue to return HOLD. Both `validate_process_case` and manifested
package audit propagate these results even when all file hashes and mass balances
are correct. This software contract does not grant scientific or engineering
approval.

## POE mass moments and historical benchmarks

IUPAC defines mass-average molar mass as the mass-fraction-weighted average of
species molar mass ([Gold Book 12217](https://goldbook.iupac.org/terms/view/12217)).
Writing species mass fraction as `n_i M_i / sum(n_j M_j)` gives
`Mw = sum(n_i M_i^2) / sum(n_i M_i)`. Average monomer mass multiplied by a chain
length second moment does not determine this quantity for compositionally
heterogeneous chains. In particular, `AA + BB` and `AB + AB` have equal length
moments but different mass second moments when `Ma != Mb`.

Commit `a06644431231e5c72362839ac6b37362a48e6218` added live and dead mass second
moments. That scientific correction is retained. The model now integrates 13
states instead of 11. The previous three POE RK4 workload results and timing costs
are consequently not comparable to this model. This is a model correction with
additional work, and no speedup is inferred from rebasing the comparison.

The permanent CI retains the original
`8719e59140202aae53cdfb80239b80dedad6767a` same-run baseline for every other
workload. `scripts/rebase_poe_performance.py` measures only the three POE cases in
a clean detached checkout of the pinned corrected commit, using the same Python,
dependencies, inputs, step sizes, repetitions and full/terminal output modes. It
records the measured source and model identity and preserves all superseded rows
in the runtime receipt. No timing, result digest or pass state is manually filled.

The corrected POE rows remain subject to exact structured-result digests, the
existing timing floors, full/terminal benefit retention and memory gates. Missing
or changed model identity fails qualification even if a digest happens to match.
The frozen alpha10 report is unchanged; only rows with independently reproduced
legacy digests and the explicit corrected-model identity are marked
`NOT_APPLICABLE` in historical comparison. This historical status does not waive
the mandatory same-model qualification gate.

Scientific tests are independent of benchmark digests: finite chain-population
enumeration checks Mw, a compound-Poisson closed form checks the mixed-monomer
mass moments during propagation, and exponential transfer checks live/dead moment
conservation. These checks establish reference-model arithmetic under the stated
chain-independent rates; they do not validate industrial parameters.
