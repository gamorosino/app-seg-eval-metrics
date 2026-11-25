<h1 align="center">CONNECTS Validation Engine</h1>

<p align="center">
  Evaluates a 3D segmentation against a ground-truth mask, computing voxel overlap (Dice, IoU, precision, recall), neighbour-tolerant, topology (Betti numbers, Euler characteristic) and connected-component metrics as JSON with QC figures.
</p>

<p align="center">
  <a href="https://github.com/brainlife/abcd-spec"><img src="https://img.shields.io/badge/ABCD_Spec-v1.1-green.svg" alt="ABCD Spec v1.1"></a>
  <a href="https://doi.org/10.25663/brainlife.app.973"><img src="https://img.shields.io/badge/Brainlife-brainlife.app.973-blue.svg" alt="Run on brainlife.io"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-see_LICENSE-lightgrey.svg" alt="License"></a>
</p>

## At a glance

<!-- brainlife-app:begin (generated from the App manifest; edit the manifest, not this block) -->

> **Evaluates a 3D segmentation against a ground-truth mask, computing voxel overlap (Dice, IoU, precision, recall), neighbour-tolerant, topology (Betti numbers, Euler characteristic) and connected-component metrics as JSON with QC figures.**

Accepts each mask as an OME-Zarr store, a volumetric parcellation, a NIfTI mask or (for the tested mask) a 3D TIFF stack, binarises both with foreground_labels (all non-zero voxels when empty) and computes the metrics from the lincbrain axonsynth metrics module, writing metrics/metrics.json and mid-slice comparison figures. Provide exactly one input for the tested mask and one for the ground truth; both must have the same shape. The neighbour-corrected metrics use the target and are for evaluation only.

| | |
|---|---|
| **Inputs** | `neuro/ome-zarr` (optional) ×2 · `neuro/parcellation/volume` (optional) ×2 · `neuro/mask` (optional) ×2 · `neuro/tiff-volume` (optional) |
| **Outputs** | `neuro/seg-eval-metrics` |
| **Container** | `gamorosino/app-seg-eval-metrics:0.3.0` |
| **Resources** | 4 GB memory · 1 h walltime |
| **Run it** | [doi.org/10.25663/brainlife.app.973](https://doi.org/10.25663/brainlife.app.973) |

#### Inputs

| Input | Datatype | Required | Description |
|---|---|---|---|
| `moving_ome_zarr` | `neuro/ome-zarr` | no | Moving/testing mask as an ome-zarr store (alternative to moving_parc). |
| `moving_parc` | `neuro/parcellation/volume` | no | Moving/testing mask as a volumetric parcellation NIfTI (alternative to moving_ome_zarr/moving_tif). |
| `moving_mask` | `neuro/mask` | no | Moving/testing mask as a NIfTI binary mask (alternative to moving_ome_zarr/moving_parc/moving_tif). |
| `moving_tif` | `neuro/tiff-volume` | no | Moving/testing mask as a 3D TIFF stack (alternative to moving_ome_zarr/moving_parc/moving_mask). |
| `gt_ome_zarr` | `neuro/ome-zarr` | no | Ground-truth mask as an ome-zarr store (alternative to gt_parc). |
| `gt_parc` | `neuro/parcellation/volume` | no | Ground-truth mask as a volumetric parcellation NIfTI (alternative to gt_ome_zarr/gt_mask). |
| `gt_mask` | `neuro/mask` | no | Ground-truth mask as a NIfTI binary mask (alternative to gt_ome_zarr/gt_parc). |

#### Outputs

| Output | Datatype | Description |
|---|---|---|
| `metrics` | `neuro/seg-eval-metrics` | Voxel, neighbor-corrected, topology, and component evaluation metrics as JSON. |

<details>
<summary><b>Parameters</b> (5)</summary>

| Parameter | Type | Default | Description |
|---|---|---|---|
| `foreground_labels` | string |  | Comma-separated integer label values treated as foreground when binarizing a parc/ome-zarr input. Empty means every nonzero voxel is foreground. |
| `zarr_level` | string | `0` | Internal ome-zarr array/group path (multiscale resolution level) to read. |
| `neighbor_rounds` | number | `2` | Number of face-neighbor dilation rounds used for the target-informed tolerance correction. |
| `include_topology` | boolean | `true` | Include Betti number / Euler characteristic comparison. |
| `include_components` | boolean | `true` | Include connected-component overlap metrics (splits/merges/matched IoU). |

</details>

<!-- brainlife-app:end -->

## Running the App

### On brainlife.io

Open the App at [doi.org/10.25663/brainlife.app.973](https://doi.org/10.25663/brainlife.app.973), choose `neuro/ome-zarr`, `neuro/parcellation/volume`, `neuro/mask`, `neuro/tiff-volume`, `neuro/ome-zarr`, `neuro/parcellation/volume`, `neuro/mask` from your project, set the parameters and press **Execute**. The results are saved to your project as `neuro/seg-eval-metrics`.

### Locally

You need [Singularity/Apptainer](https://apptainer.org/) (the App runs in `gamorosino/app-seg-eval-metrics:0.3.0`), [`jq`](https://jqlang.github.io/jq/).

1. Clone this repository.
2. Create `config.json` with the paths to your inputs and the parameters:

   ```json
   {
       "moving_ome_zarr": "/path/to/moving_ome_zarr/moving_ome_zarr",
       "moving_parc": "/path/to/moving_parc/moving_parc",
       "moving_mask": "/path/to/moving_mask/moving_mask",
       "moving_tif": "/path/to/moving_tif/moving_tif",
       "gt_ome_zarr": "/path/to/gt_ome_zarr/gt_ome_zarr",
       "gt_parc": "/path/to/gt_parc/gt_parc",
       "gt_mask": "/path/to/gt_mask/gt_mask",
       "foreground_labels": "",
       "zarr_level": "0",
       "neighbor_rounds": 2,
       "include_topology": true,
       "include_components": true
   }
   ```

3. Run `./main`.

## Configuration parameters

| Parameter            | Type    | Default | Description                                                                                   |
| -------------------- | ------- | ------- | --------------------------------------------------------------------------------------------- |
| `foreground_labels`  | string  | `""`    | Comma-separated integer labels treated as foreground when binarizing. Empty = all nonzero.    |
| `zarr_level`         | string  | `"0"`   | Internal ome-zarr resolution level to read (multiscale path).                                 |
| `neighbor_rounds`    | number  | `2`     | Face-neighbor dilation rounds for the target-informed tolerance correction.                   |
| `include_topology`   | boolean | `true`  | Include Betti number / Euler characteristic comparison.                                       |
| `include_components` | boolean | `true`  | Include connected-component overlap metrics (splits, merges, matched IoU).                    |

---

## Container

```
docker://gamorosino/app-seg-eval-metrics:0.2
```

---

## Citing

If you use this App, please cite it, the software it builds on and brainlife.io:

- CONNECTS Validation Engine. brainlife.io App. [doi:10.25663/brainlife.app.973](https://doi.org/10.25663/brainlife.app.973)
- Hayashi S, Caron BA, Heinsfeld AS, et al. brainlife.io: a decentralized and open-source cloud platform to support neuroscience research. *Nature Methods* 21:809–813 (2024). [doi:10.1038/s41592-024-02237-2](https://doi.org/10.1038/s41592-024-02237-2)
- Avesani P, McPherson B, Hayashi S, et al. The open diffusion data derivatives, brain data upcycling via integrated publishing of derivatives and reproducible open cloud services. *Scientific Data* 6:69 (2019). [doi:10.1038/s41597-019-0073-y](https://doi.org/10.1038/s41597-019-0073-y)

## Authors

**Gabriele Amorosino**

---

## License

See [LICENSE](LICENSE).
