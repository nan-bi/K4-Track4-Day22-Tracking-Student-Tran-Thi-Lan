"""Unit tests for evaluate_practice.py pure functions."""

import json
from pathlib import Path

import numpy as np
import pytest

from evaluate_practice import _load_eval_config, _patch_numpy_aliases, stage


def test_patch_numpy_aliases() -> None:
    """Kiểm tra patch np.float và np.int tồn tại."""
    _patch_numpy_aliases()
    assert hasattr(np, "float")
    assert hasattr(np, "int")


def test_load_eval_config_success(tmp_path: Path) -> None:
    """Kiểm tra đọc eval_config.json thành công."""
    v1_dir = tmp_path / "video_1"
    v1_dir.mkdir(parents=True)
    cfg_data = {"benchmark": "MOT17", "split": "train"}
    (v1_dir / "eval_config.json").write_text(json.dumps(cfg_data), encoding="utf-8")

    loaded = _load_eval_config(tmp_path)
    assert loaded["benchmark"] == "MOT17"
    assert loaded["split"] == "train"


def test_load_eval_config_missing_raises(tmp_path: Path) -> None:
    """Kiểm tra báo lỗi khi thiếu eval_config.json."""
    with pytest.raises(FileNotFoundError, match="Không thấy"):
        _load_eval_config(tmp_path)


def test_stage_missing_gt_raises(tmp_path: Path) -> None:
    """Kiểm tra stage báo lỗi khi thiếu file gt hoặc seqinfo.ini."""
    lab_data = tmp_path / "lab_data"
    lab_data.mkdir()
    trackeval = tmp_path / "trackeval"
    trackeval.mkdir()
    sub = tmp_path / "video_1.txt"
    sub.write_text("1,1,0,0,10,10,1,-1,-1,-1\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="thiếu gt hoặc seqinfo"):
        stage(trackeval, lab_data, sub, "test_run", "MOT17")


def test_stage_missing_submission_raises(tmp_path: Path) -> None:
    """Kiểm tra stage báo lỗi khi không thấy file submission."""
    lab_data = tmp_path / "lab_data"
    v1 = lab_data / "video_1"
    (v1 / "gt").mkdir(parents=True)
    (v1 / "gt" / "gt.txt").write_text("1,1,0,0,10,10,1,1,1\n", encoding="utf-8")
    (v1 / "seqinfo.ini").write_text("[Sequence]\nname=video_1\n", encoding="utf-8")

    trackeval = tmp_path / "trackeval"
    trackeval.mkdir()
    missing_sub = tmp_path / "missing_video_1.txt"

    with pytest.raises(FileNotFoundError, match="Không thấy file nộp"):
        stage(trackeval, lab_data, missing_sub, "test_run", "MOT17")


def test_stage_success(tmp_path: Path) -> None:
    """Kiểm tra stage copy file đúng cấu trúc thư mục TrackEval."""
    lab_data = tmp_path / "lab_data"
    v1 = lab_data / "video_1"
    (v1 / "gt").mkdir(parents=True)
    (v1 / "gt" / "gt.txt").write_text("1,1,0,0,10,10,1,1,1\n", encoding="utf-8")
    (v1 / "seqinfo.ini").write_text("[Sequence]\nname=video_1\n", encoding="utf-8")

    trackeval = tmp_path / "trackeval"
    trackeval.mkdir()
    sub = tmp_path / "video_1.txt"
    sub.write_text("1,1,0,0,10,10,1,-1,-1,-1\n", encoding="utf-8")

    stage(trackeval, lab_data, sub, "run_01", "MOT17")

    expected_gt = trackeval / "data" / "gt" / "mot_challenge" / "MOT17-train" / "video_1" / "gt" / "gt.txt"
    expected_seq = trackeval / "data" / "gt" / "mot_challenge" / "MOT17-train" / "video_1" / "seqinfo.ini"
    expected_sub = trackeval / "data" / "trackers" / "mot_challenge" / "MOT17-train" / "run_01" / "data" / "video_1.txt"

    assert expected_gt.exists()
    assert expected_seq.exists()
    assert expected_sub.exists()
