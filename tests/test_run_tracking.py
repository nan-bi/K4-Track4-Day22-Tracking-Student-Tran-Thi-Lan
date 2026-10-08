"""Unit tests for run_tracking.py pure functions."""

from pathlib import Path

import cv2
import numpy as np
import pytest

from run_tracking import color_for_id, iter_frames


def test_color_for_id_deterministic() -> None:
    """Kiểm tra color_for_id sinh màu nhất quán cho cùng một track_id."""
    c1 = color_for_id(42)
    c2 = color_for_id(42)
    assert c1 == c2
    assert len(c1) == 3


def test_color_for_id_value_range() -> None:
    """Kiểm tra các kênh màu BGR nằm trong khoảng 64..254."""
    for track_id in [0, 1, 5, 99, 12345]:
        color = color_for_id(track_id)
        assert len(color) == 3
        for val in color:
            assert 64 <= val <= 254


def test_color_for_id_different_ids() -> None:
    """Kiểm tra các ID khác nhau sinh ra màu khác nhau."""
    c1 = color_for_id(1)
    c2 = color_for_id(2)
    assert c1 != c2


def test_iter_frames_from_image_dir(tmp_path: Path) -> None:
    """Kiểm tra iter_frames đọc đúng danh sách ảnh theo thứ tự tăng dần."""
    img_dir = tmp_path / "img1"
    img_dir.mkdir(parents=True)

    # Tạo 3 ảnh mẫu nhỏ 10x10
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    cv2.imwrite(str(img_dir / "000001.jpg"), img)
    cv2.imwrite(str(img_dir / "000002.jpg"), img)
    cv2.imwrite(str(img_dir / "000003.jpg"), img)

    frames = list(iter_frames(img_dir))
    assert len(frames) == 3
    assert frames[0][0] == 0
    assert frames[1][0] == 1
    assert frames[2][0] == 2
    assert frames[0][1].shape == (10, 10, 3)


def test_iter_frames_empty_dir_raises(tmp_path: Path) -> None:
    """Kiểm tra iter_frames báo lỗi khi thư mục không có ảnh .jpg."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    with pytest.raises(FileNotFoundError, match="Không tìm thấy ảnh .jpg"):
        list(iter_frames(empty_dir))


def test_iter_frames_nonexistent_file_raises(tmp_path: Path) -> None:
    """Kiểm tra iter_frames báo lỗi khi file video không tồn tại."""
    fake_video = tmp_path / "fake.mp4"
    with pytest.raises(FileNotFoundError, match="Không mở được video"):
        list(iter_frames(fake_video))
