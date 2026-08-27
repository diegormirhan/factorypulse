# AI4I 2020 Data Card

## Source

Matzka, S. (2020). *AI4I 2020 Predictive Maintenance Dataset* [Dataset]. UCI Machine Learning Repository. DOI: [10.24432/C5HS5C](https://doi.org/10.24432/C5HS5C).

The dataset is licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

## Motivation and composition

Real predictive-maintenance data is difficult to publish, so AI4I was designed as a synthetic approximation of industrial operating data. It contains 10,000 records, six usable predictor columns, one machine-failure target, and five failure-mode targets. There are no missing values.

The binary target is imbalanced: 339 records, or 3.39%, are labeled as failures.

## Fields used by FactoryPulse

| Original field | Canonical field | Role | Unit |
|---|---|---|---|
| Type | `product_type` | feature | L, M, H |
| Air temperature [K] | `air_temperature_k` | feature | K |
| Process temperature [K] | `process_temperature_k` | feature | K |
| Rotational speed [rpm] | `rotational_speed_rpm` | feature | rpm |
| Torque [Nm] | `torque_nm` | feature | Nm |
| Tool wear [min] | `tool_wear_min` | feature | min |
| Machine failure | `machine_failure` | target | binary |

## Excluded fields

- UDI is a row identifier.
- Product ID combines product grade with a serial value and is unnecessary for the intended generalization.
- TWF, HDF, PWF, OSF, and RNF encode target failure modes. Using them as input would leak the answer into the model.

## Processing

FactoryPulse validates column presence, product grades, numeric conversion, missing values, and target values. The model pipeline derives temperature gap, mechanical power, and wear-load index after splitting, so preprocessing stays part of the serialized estimator.

## Known limitations

- The dataset is synthetic, not collected from physical equipment.
- Records do not include machine identity, timestamp, maintenance action, downtime, or delayed outcomes.
- Product grades are generated categories and should not be interpreted as real manufacturer quality labels.
- The failure mechanisms used to synthesize labels may make the benchmark easier than real failure prediction.
- Random train/test splitting cannot measure temporal or cross-site generalization.

