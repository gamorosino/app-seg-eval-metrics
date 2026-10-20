#!/usr/bin/env python3
"""brainlife.io entrypoint: binary-mask evaluation metrics.

Reads a "moving/testing" mask and a ground-truth mask and writes the metrics
from `evaluate_binary_mask` to metrics/metrics.json, after binarizing both
against `foreground_labels`. The ground-truth mask may be an `ome-zarr` store,
a `parc` (volumetric parcellation) NIfTI, or a NIfTI binary `mask`; the
moving/testing mask may additionally be a 3D TIFF stack.
"""
from __future__ import annotations

import base64
import io
import json
import os
import tempfile
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import tifffile
import zarr

from metrics import evaluate_binary_mask

CONFIG_PATH = "config.json"
OUTPUT_DIR = "metrics"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "metrics.json")
PRODUCT_PATH = "product.json"

_TP_COLOR = np.array([0, 200, 80], dtype=np.uint8)    # green
_FP_COLOR = np.array([255, 200, 0], dtype=np.uint8)   # yellow
_FN_COLOR = np.array([220, 60, 60], dtype=np.uint8)   # red
_GT_COLOR = np.array([40, 120, 255], dtype=np.uint8)  # blue


def _parse_labels(raw: str) -> list[int]:
    raw = raw.strip()
    if not raw:
        return []
    return [int(token) for token in raw.split(",") if token.strip()]


def _binarize(data: np.ndarray, labels: list[int]) -> np.ndarray:
    if not labels:
        return data != 0
    return np.isin(data, labels)


def _resolve_path(path: str) -> str:
    """Download remote URLs to a temp file; return local paths unchanged."""
    # brainlife may pass the URL with a single slash (https:/...) after path normalization
    normalized = path if "://" in path else path.replace(":/", "://", 1)
    if normalized.startswith(("http://", "https://")):
        suffix = os.path.splitext(path)[-1] or ".nii.gz"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        urllib.request.urlretrieve(normalized, tmp.name)
        return tmp.name
    return path


def _load_parc(path: str, labels: list[int]) -> np.ndarray:
    data = np.asarray(nib.load(_resolve_path(path)).get_fdata())
    return _binarize(data, labels)


def _load_ome_zarr(path: str, level: str, labels: list[int]) -> np.ndarray:
    group = zarr.open(_resolve_path(path), mode="r")
    array = group[level] if hasattr(group, "__getitem__") and level in group else group
    data = np.asarray(array)
    return _binarize(data, labels)


def _load_tif(path: str, labels: list[int]) -> np.ndarray:
    data = np.asarray(tifffile.imread(_resolve_path(path)))
    return _binarize(data, labels)


def _load_mask(
    config: dict, prefix: str, level: str, labels: list[int], allow_tif: bool = False
) -> np.ndarray:
    zarr_path = config.get(f"{prefix}_ome_zarr")
    parc_path = config.get(f"{prefix}_parc")
    mask_path = config.get(f"{prefix}_mask")
    tif_path = config.get(f"{prefix}_tif") if allow_tif else None
    if zarr_path:
        return _load_ome_zarr(zarr_path, level, labels)
    if parc_path:
        return _load_parc(parc_path, labels)
    if mask_path:
        return _load_parc(mask_path, labels)
    if tif_path:
        return _load_tif(tif_path, labels)
    options = f"'{prefix}_ome_zarr', '{prefix}_parc', '{prefix}_mask'" + (
        f", or '{prefix}_tif'" if allow_tif else ""
    )
    raise ValueError(f"no input provided for '{prefix}': set one of {options} in config.json")


def _mask_to_rgb(mask: np.ndarray, color: np.ndarray) -> np.ndarray:
    rgb = np.zeros((*mask.shape, 3), dtype=np.uint8)
    rgb[mask.astype(bool)] = color
    return rgb


def _overlay_rgb(pred: np.ndarray, target: np.ndarray) -> np.ndarray:
    rgb = np.zeros((*pred.shape, 3), dtype=np.uint8)
    rgb[pred & target] = _TP_COLOR
    rgb[pred & ~target] = _FP_COLOR
    rgb[~pred & target] = _FN_COLOR
    return rgb


def _fig_to_b64(fig: "plt.Figure") -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def _make_qc_images(prediction: np.ndarray, target: np.ndarray) -> list[dict]:
    pred_b = prediction.astype(bool)
    gt_b = target.astype(bool)
    mid = [s // 2 for s in pred_b.shape]
    axes_info = [
        ("axial",    (mid[0], slice(None), slice(None))),
        ("coronal",  (slice(None), mid[1], slice(None))),
        ("sagittal", (slice(None), slice(None), mid[2])),
    ]
    col_titles = ["Ground truth", "Prediction", "TP / FP / FN"]
    entries = []
    for axis_name, idx in axes_info:
        gt_sl   = gt_b[idx]
        pred_sl = pred_b[idx]
        panels = [
            _mask_to_rgb(gt_sl, _GT_COLOR),
            _mask_to_rgb(pred_sl, _TP_COLOR),
            _overlay_rgb(pred_sl, gt_sl),
        ]
        fig, axs = plt.subplots(1, 3, figsize=(12, 4))
        for ax, panel, title in zip(axs, panels, col_titles):
            ax.imshow(panel, interpolation="nearest")
            ax.set_title(title, fontsize=11)
            ax.axis("off")
        fig.suptitle(f"Mid-slice — {axis_name}", fontsize=13)
        fig.tight_layout()
        entries.append({"type": "image/png", "name": f"qc_{axis_name}", "base64": _fig_to_b64(fig)})
        plt.close(fig)
    return entries


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

    qc_images = _make_qc_images(prediction, target)
    with open(PRODUCT_PATH, "w") as f:
        json.dump({"brainlife": qc_images}, f)


if __name__ == "__main__":
    main()
