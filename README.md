# CONNECTS Validation Engine

`app-seg-eval-metrics`

Voxel, target-informed neighbor-corrected, topology, and connected-component metrics comparing a **moving/testing** 3D binary mask against a **ground-truth** mask.

---

# Author

**Gabriele Amorosino** ([gabriele.amorosino@utexas.edu](mailto:gabriele.amorosino@utexas.edu))

---

# Overview

The app binarizes both masks against `foreground_labels` (every nonzero voxel when empty) and computes a comprehensive set of segmentation evaluation metrics:

| Metric group            | Description                                                              |
| ----------------------- | ------------------------------------------------------------------------ |
| Voxel overlap           | Dice, IoU, precision, recall, F1 and related overlap scores              |
| Neighbor-corrected      | Target-informed tolerance correction via face-neighbor dilation          |
| Topology                | Betti numbers and Euler characteristic comparison (optional)             |
| Connected components    | Split/merge counts and matched-component IoU (optional)                  |

Both masks are binarized to the same shape before evaluation. Remote URLs are downloaded automatically before loading.

---

# Inputs

Provide exactly **one** input per mask — whichever datatype it actually is:

| Config key       | Datatype                      | Description                                        |
| ---------------- | ----------------------------- | -------------------------------------------------- |
| `moving_ome_zarr`| `neuro/ome-zarr`              | Moving mask as an ome-zarr store                   |
| `moving_parc`    | `neuro/parcellation/volume`   | Moving mask as a volumetric parcellation NIfTI     |
| `moving_mask`    | `neuro/mask`                  | Moving mask as a NIfTI binary mask                 |
| `moving_tif`     | `neuro/tiff-volume`           | Moving mask as a 3D TIFF stack                     |
| `gt_ome_zarr`    | `neuro/ome-zarr`              | Ground-truth mask as an ome-zarr store             |
| `gt_parc`        | `neuro/parcellation/volume`   | Ground-truth mask as a volumetric parcellation NIfTI|
| `gt_mask`        | `neuro/mask`                  | Ground-truth mask as a NIfTI binary mask           |

All inputs are optional in the schema — the app raises a clear error if neither side has a valid input.

---

# Outputs

| Output    | Datatype                | Description                                      |
| --------- | ----------------------- | ------------------------------------------------ |
| `metrics` | `neuro/seg-eval-metrics`| Evaluation metrics as JSON (`metrics/metrics.json`) |

QC mid-slice comparison figures (axial, coronal, sagittal) are written to `figures/` and assembled into `product.json` for the brainlife.io viewer.

---

# Configuration parameters

| Parameter            | Type    | Default | Description                                                                                   |
| -------------------- | ------- | ------- | --------------------------------------------------------------------------------------------- |
| `foreground_labels`  | string  | `""`    | Comma-separated integer labels treated as foreground when binarizing. Empty = all nonzero.    |
| `zarr_level`         | string  | `"0"`   | Internal ome-zarr resolution level to read (multiscale path).                                 |
| `neighbor_rounds`    | number  | `2`     | Face-neighbor dilation rounds for the target-informed tolerance correction.                   |
| `include_topology`   | boolean | `true`  | Include Betti number / Euler characteristic comparison.                                       |
| `include_components` | boolean | `true`  | Include connected-component overlap metrics (splits, merges, matched IoU).                    |

---

# Running the app

## Brainlife

Run through the Brainlife web UI or submit programmatically via `faber-app-run` / `faber-app-pipeline`.

---

## Running locally

Clone the repository and copy the example config:

```bash
git clone https://github.com/gamorosino/app-seg-eval-metrics.git
cd app-seg-eval-metrics
cp config.json.example config.json
```

Edit `config.json` with real file paths, then:

```bash
chmod +x main
./main
```

`main` pulls its own container (`singularity exec docker://gamorosino/app-seg-eval-metrics:0.2`) — no local Python install needed, only Singularity.

---

# Container

```
docker://gamorosino/app-seg-eval-metrics:0.2
```

---

# License

MIT, see `LICENSE`, except `metrics.py`, which is vendored verbatim from
[lincbrain/axonsynth](https://github.com/lincbrain/axonsynth/blob/main/paper_analysis/metrics.py)
with the maintainer's permission. That upstream repo has no LICENSE file of
its own; see the header of `metrics.py` for details.
