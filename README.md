# CONNECTS Validation Engine

<!-- brainlife-app:begin (generated from the App manifest; edit the manifest, not this block) -->

> **Evaluates a 3D segmentation against a ground-truth mask, computing voxel overlap (Dice, IoU, precision, recall), neighbour-tolerant, topology (Betti numbers, Euler characteristic) and connected-component metrics as JSON with QC figures.**

Accepts each mask as an OME-Zarr store, a volumetric parcellation, a NIfTI mask or (for the tested mask) a 3D TIFF stack, binarises both with foreground_labels (all non-zero voxels when empty) and computes the metrics from the lincbrain axonsynth metrics module, writing metrics/metrics.json and mid-slice comparison figures. Provide exactly one input for the tested mask and one for the ground truth; both must have the same shape. The neighbour-corrected metrics use the target and are for evaluation only.

| | |
|---|---|
| 📥 **Inputs** | `neuro/ome-zarr` (optional) ×2 · `neuro/parcellation/volume` (optional) ×2 · `neuro/mask` (optional) ×2 · `neuro/tiff-volume` (optional) |
| 📤 **Outputs** | `neuro/seg-eval-metrics` |
| 🐳 **Container** | `gamorosino/app-seg-eval-metrics:0.3.0` |
| ⚙️ **Resources** | 4 GB memory · 1 h walltime |
| 🔗 **Run it** | [doi.org/10.25663/brainlife.app.973](https://doi.org/10.25663/brainlife.app.973) |

#### 📥 Inputs

| Input | Datatype | Required | Description |
|---|---|---|---|
| `moving_ome_zarr` | `neuro/ome-zarr` | no | Moving/testing mask as an ome-zarr store (alternative to moving_parc). |
| `moving_parc` | `neuro/parcellation/volume` | no | Moving/testing mask as a volumetric parcellation NIfTI (alternative to moving_ome_zarr/moving_tif). |
| `moving_mask` | `neuro/mask` | no | Moving/testing mask as a NIfTI binary mask (alternative to moving_ome_zarr/moving_parc/moving_tif). |
| `moving_tif` | `neuro/tiff-volume` | no | Moving/testing mask as a 3D TIFF stack (alternative to moving_ome_zarr/moving_parc/moving_mask). |
| `gt_ome_zarr` | `neuro/ome-zarr` | no | Ground-truth mask as an ome-zarr store (alternative to gt_parc). |
| `gt_parc` | `neuro/parcellation/volume` | no | Ground-truth mask as a volumetric parcellation NIfTI (alternative to gt_ome_zarr/gt_mask). |
| `gt_mask` | `neuro/mask` | no | Ground-truth mask as a NIfTI binary mask (alternative to gt_ome_zarr/gt_parc). |

#### 📤 Outputs

| Output | Datatype | Description |
|---|---|---|
| `metrics` | `neuro/seg-eval-metrics` | Voxel, neighbor-corrected, topology, and component evaluation metrics as JSON. |

<details>
<summary><b>⚙️ Parameters</b> (5)</summary>

| Parameter | Type | Default | Description |
|---|---|---|---|
| `foreground_labels` | string |  | Comma-separated integer label values treated as foreground when binarizing a parc/ome-zarr input. Empty means every nonzero voxel is foreground. |
| `zarr_level` | string | `0` | Internal ome-zarr array/group path (multiscale resolution level) to read. |
| `neighbor_rounds` | number | `2` | Number of face-neighbor dilation rounds used for the target-informed tolerance correction. |
| `include_topology` | boolean | `true` | Include Betti number / Euler characteristic comparison. |
| `include_components` | boolean | `true` | Include connected-component overlap metrics (splits/merges/matched IoU). |

</details>

<!-- brainlife-app:end -->

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
