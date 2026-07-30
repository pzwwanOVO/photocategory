"""安全文件操作：完整性校验、目录创建、冲突重命名、移动归位。"""
import os
import shutil


def verify_integrity(path, expected_size):
    """校验本地文件完整性。expected_size 为 None 时仅检查存在性。"""
    if not os.path.exists(path):
        return False, "文件不存在"
    if expected_size is None:
        return True, "ok"
    try:
        actual = os.path.getsize(path)
    except OSError as e:
        return False, f"无法读取大小：{e}"
    if actual != expected_size:
        return False, f"大小不匹配：期望 {expected_size}，实际 {actual}"
    return True, "ok"


def resolve_collision(path):
    """若目标路径已存在，追加 _2/_3 后缀返回新路径。"""
    if not os.path.exists(path):
        return path
    directory = os.path.dirname(path)
    stem, ext = os.path.splitext(os.path.basename(path))
    # 长截图后缀保留
    long_suffix = ""
    if stem.endswith("_long"):
        stem = stem[: -len("_long")]
        long_suffix = "_long"
    idx = 2
    while True:
        candidate = os.path.join(directory, f"{stem}_{idx}{long_suffix}{ext}")
        if not os.path.exists(candidate):
            return candidate
        idx += 1


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def move_to_final(staging_path, target_root, rel_target, new_name):
    """将暂存文件移动到最终分类目录，处理重名冲突。

    rel_target: 目标根之下的文件夹路径段列表
    new_name: 最终文件名（含扩展名）
    返回最终绝对路径。
    """
    dest_dir = os.path.join(target_root, *rel_target)
    ensure_dir(dest_dir)
    final_path = os.path.join(dest_dir, new_name)
    final_path = resolve_collision(final_path)
    shutil.move(staging_path, final_path)
    return final_path


def safe_remove(path):
    """安全删除（忽略错误）。"""
    try:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.remove(path)
        return True
    except Exception:
        return False
