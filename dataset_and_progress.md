# Photometric Redshift Prediction — Project Progress

## Project Goal

The aim of this project is to investigate whether an Artificial Neural Network (ANN) can predict galaxy photometric redshifts from JWST/HST photometric measurements.

The ANN will ultimately be compared against:

* Classical machine-learning approaches such as Random Forest and XGBoost.
* The template-fitting method LePHARE.
* Spectroscopic redshifts (`z_spec`) as the reference/ground-truth measurements.

The main evaluation will therefore be performed on galaxies for which reliable spectroscopic redshifts are available.

---

## CEERS Photometric Dataset

The primary photometric dataset is the CEERS catalog:

`ceers_cat_v1.0.fits`

It contains **87,345 sources** and photometric measurements from 14 filters.

### JWST/NIRCam

* F115W
* F150W
* F200W
* F277W
* F356W
* F410M
* F444W

### HST

* F435W
* F606W
* F814W
* F105W
* F125W
* F140W
* F160W

For the ML models, the main candidate features are the fluxes and corresponding flux uncertainties from these filters.

The catalog also provides LePHARE photometric-redshift estimates, including:

* `LP_Z_MED`
* `LP_Z_BEST`

These values will be used as a benchmark rather than as the training target.

---

## Spectroscopic Redshift Dataset

The CEERS catalog does not contain a direct spectroscopic-redshift column. Therefore, an external spectroscopic catalog was required.

The CANDELS EGS redshift catalog was selected because it covers the same Extended Groth Strip region and provides:

* Right Ascension
* Declination
* Spectroscopic redshift (`z_spec`)
* Spectroscopic-redshift reference
* Best-redshift type
* Other photometric/grism redshift information

After removing objects without valid spectroscopic redshifts:

**2,540 objects have valid spectroscopic redshifts.**

---

## CEERS–Spectroscopic Cross-Matching

The CEERS and CANDELS catalogs were cross-matched using their RA and DEC sky coordinates with Astropy.

Using an initial matching radius of **0.3 arcseconds**:

* CEERS sources: **87,345**
* Valid spectroscopic sources: **2,540**
* Initial matches: **1,204**
* Unique one-to-one matches: **1,180**
* Duplicate spectroscopic assignments removed: **24**

The current supervised dataset therefore contains approximately **1,180 galaxies** with both CEERS photometry and spectroscopic redshifts.

---

## Astrometric Offset

Analysis of the matched coordinates revealed a systematic positional offset between the two catalogs.

Median offsets:

* ΔRA ≈ **−0.025 arcsec**
* ΔDEC ≈ **−0.195 arcsec**

The declination offset explains why relatively few objects match at very small matching radii.

For example:

| Matching radius | Matches |
| --------------- | ------: |
| 0.10″           |      20 |
| 0.15″           |      76 |
| 0.20″           |     540 |
| 0.25″           |   1,108 |
| 0.30″           |   1,204 |
| 0.50″           |   1,367 |
| 1.00″           |   1,932 |

The next cross-matching step will correct this systematic offset and then use a tighter matching radius to obtain a cleaner final spectroscopic sample.

---

## Spectroscopic Redshift Distribution

The current unique matched sample contains:

| Redshift      | Galaxies |
| ------------- | -------: |
| 0 < z ≤ 0.5   |      277 |
| 0.5 < z ≤ 1.0 |      461 |
| 1.0 < z ≤ 1.5 |      261 |
| 1.5 < z ≤ 2.0 |       60 |
| 2.0 < z ≤ 3.0 |      100 |
| 3.0 < z ≤ 4.0 |       21 |
| z > 4         |        0 |

The spectroscopic training sample is therefore strongly concentrated at lower redshifts.

This is an important limitation because the trained models cannot be assumed to generalize reliably to the high-redshift CEERS population without additional high-redshift spectroscopic training data.

---

## Current LePHARE Baseline

LePHARE predictions were compared against the available spectroscopic redshifts.

There are **1,173 objects** with both a valid spectroscopic redshift and usable LePHARE median redshift.

Current results:

* Mean absolute redshift error: **0.127**
* Median `|Δz / (1 + z_spec)|`: **0.0270**
* `σ_NMAD`: **0.0315**
* Catastrophic outlier fraction: **7.08%**

where:

`Δz = z_phot − z_spec`

These results provide an initial benchmark against which the machine-learning models can eventually be compared.

---

# Next Steps

## 1. Finalise the Cross-Match

Correct the systematic RA/DEC offset between CEERS and CANDELS and repeat the coordinate matching with a tighter radius.

Then:

* Remove ambiguous matches.
* Enforce one-to-one matching.
* Verify spectroscopic-redshift provenance.
* Produce the final spectroscopic training dataset.

## 2. Prepare ML Features

Create a clean feature matrix containing the JWST/HST photometric measurements.

Potential inputs include:

`14 filter fluxes + corresponding flux uncertainties`

Missing photometry, invalid/sentinel values and non-detections will need to be handled carefully.

## 3. Create Train/Validation/Test Sets

The spectroscopically confirmed sample will be divided into training, validation and test subsets.

The test set must remain unseen during model development.

All models, including LePHARE, should ultimately be evaluated on the **same test galaxies** for a fair comparison.

## 4. Train Baseline ML Models

Train classical machine-learning models such as:

* Random Forest
* XGBoost

These provide useful baselines for determining whether a neural network provides a meaningful improvement.

## 5. Train Artificial Neural Network

Train an ANN using CEERS photometric measurements as input:

`JWST/HST photometry → ANN → predicted redshift`

with:

`z_spec`

as the supervised target.

## 6. Final Evaluation

Compare:

`ANN vs Random Forest/XGBoost vs LePHARE`

using metrics such as:

* MAE
* RMSE
* Bias
* `σ_NMAD`
* Catastrophic outlier fraction

Performance should also be examined across different redshift ranges because the available spectroscopic sample is highly imbalanced toward lower-redshift galaxies.

---

## Current Status

**CEERS catalog obtained → spectroscopic catalog obtained → catalogs cross-matched → systematic astrometric offset identified → LePHARE baseline established → next step: finalise cross-match and prepare the ML dataset.**
