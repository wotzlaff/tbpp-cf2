# Compact Models for the Temporal Bin Packing Problem with Fire-Ups

This repository contains compact models for the Temporal Bin Packing Problem with Fire-Ups.
The problem was introduced in [[1]](#1).
Some improvements for the basic models were proposed in [[2]](#2).

The models in this repository are improved even more. A description of the improvements will be published soon.

## Examples

You can find two example files in the `examples` directory.

## Installation

The file `environment.yml` contains a description of all required packages.
You can create a clean conda environment from this file using

```
conda env create
```

and activate it using

```
conda activate grb
```

Afterwards, use

```
conda develop .
```

to setup a link to the `tbpp_cf2` package such that it can be loaded easily.

## Data of Benchmark Instances

The data for the benchmark instances can be found [here](https://github.com/sibirbil/TemporalBinPacking).

## References

<a id="1">[1]</a>
Aydın, N., Muter, İ., & Birbil, Ş. İ. (2020). Multi-objective temporal bin packing problem: An application in cloud computing. Computers & Operations Research, 121, 104959.
<a id="2">[2]</a>
Martinovic, J., Strasdat, N., & Selch, M. (2021). Compact integer linear programming formulations for the temporal bin packing problem with fire-ups. Computers & Operations Research, 105288.
