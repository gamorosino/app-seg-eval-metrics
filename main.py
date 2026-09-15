#!/usr/bin/env python3
"""brainlife.io entrypoint: binary-mask evaluation metrics.

Reads a "moving/testing" mask and a ground-truth mask and writes the metrics
from `evaluate_binary_mask` to metrics/metrics.json, after binarizing both
against `foreground_labels`. The ground-truth mask may be an `ome-zarr` store
or a `parc` (volumetric parcellation) NIfTI; the moving/testing mask may
additionally be a 3D TIFF stack.
"""
from __future__ import annotations

import json
import os

import nibabel as nib
import numpy as np
import tifffile
import zarr

from metrics import evaluate_binary_mask

CONFIG_PATH = "config.json"
OUTPUT_DIR = "metrics"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "metrics.json")


def _parse_labels(raw: str) -> list[int]:
    raw = raw.strip()
    if not raw:
        return []
    return [int(token) for token in raw.split(",") if token.strip()]


def _binarize(data: np.ndarray, labels: list[int]) -> np.ndarray:
    if not labels:
        return data != 0
    return np.isin(data, labels)


def _load_parc(path: str, labels: list[int]) -> np.ndarray:
    data = np.asarray(nib.load(path).get_fdata())
    return _binarize(data, labels)


def _load_ome_zarr(path: str, level: str, labels: list[int]) -> np.ndarray:
    group = zarr.open(path, mode="r")
    array = group[level] if hasattr(group, "__getitem__") and level in group else group
    data = np.asarray(array)
    return _binarize(data, labels)


def _load_tif(path: str, labels: list[int]) -> np.ndarray:
    data = np.asarray(tifffile.imread(path))
    return _binarize(data, labels)


def _load_mask(
    config: dict, prefix: str, level: str, labels: list[int], allow_tif: bool = False
) -> np.ndarray:
    zarr_path = config.get(f"{prefix}_ome_zarr")
    parc_path = config.get(f"{prefix}_parc")
    tif_path = config.get(f"{prefix}_tif") if allow_tif else None
    if zarr_path:
        return _load_ome_zarr(zarr_path, level, labels)
    if parc_path:
        return _load_parc(parc_path, labels)
    if tif_path:
        return _load_tif(tif_path, labels)
    options = f"'{prefix}_ome_zarr', '{prefix}_parc'" + (
        f", or '{prefix}_tif'" if allow_tif else ""
    )
    raise ValueError(f"no input provided for '{prefix}': set one of {options} in config.json")


def main() -> None:
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    labels = _parse_labels(str(config.get("foreground_labels", "")))
    zarr_level = str(config.get("zarr_level", "0"))

    prediction = _load_mask(config, "moving", zarr_level, labels, allow_tif=True)
    target = _load_mask(config, "gt", zarr_level, labels)

    result = evaluate_binary_mask(
        prediction,
        target,
        neighbor_rounds=int(config.get("neighbor_rounds", 2)),
        include_topology=bool(config.get("include_topology", True)),
        include_components=bool(config.get("include_components", True)),
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
