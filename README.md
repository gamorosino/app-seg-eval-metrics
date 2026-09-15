# seg-eval-metrics

Voxel, target-informed neighbor-corrected, topology, and connected-component metrics comparing a moving/testing 3D binary mask against a ground-truth mask. The ground-truth mask may be an ome-zarr store or a parc (volumetric parcellation) NIfTI; the moving/testing mask may additionally be a 3D TIFF stack.

## Inputs

Provide exactly one input per mask -- whichever datatype it actually is:

- `moving_ome_zarr` (neuro/ome-zarr) -- optional
- `moving_parc` (neuro/parcellation/volume) -- optional
- `moving_tif` (neuro/tiff-volume) -- optional
- `gt_ome_zarr` (neuro/ome-zarr) -- optional
- `gt_parc` (neuro/parcellation/volume) -- optional

Both masks are binarized against `foreground_labels` (nonzero == foreground
when empty) and must resolve to arrays of the same shape.

## Outputs

- `metrics` (neuro/seg-eval-metrics) -- Voxel, neighbor-corrected, topology, and component evaluation metrics as JSON.

## Usage

Brainlife.io: run via `braise-app-run`/`braise-app-pipeline` (once registered
with `braise-app-create`), or the web UI.

Locally (outside brainlife): copy `config.json.example` to `config.json`,
fill in real file paths, then run `./main` from this directory. `main` pulls
its own container (`singularity exec docker://...`) -- no local install of
the underlying tool needed, only Singularity itself.

Entrypoint: `main.py`

## Authors

- Gabriele Amorosino <ga24643@eid.utexas.edu>

## License

MIT, see `LICENSE`, except `metrics.py`, which is vendored verbatim from
[lincbrain/axonsynth](https://github.com/lincbrain/axonsynth/blob/main/paper_analysis/metrics.py)
with the maintainer's permission. That upstream repo has no LICENSE file of
its own; see the header of `metrics.py` for details.
