"""
أدوات مساعدة - Helper Utilities
"""

import os
import uuid
from werkzeug.utils import secure_filename


# ── حفظ الصورة المرفوعة ────────────────────────────────────────────────────────
def save_image(file, config: dict) -> str | None:
    """
    يحفظ الصورة في UPLOAD_FOLDER ويعيد المسار النسبي.
    يعيد None لو نوع الملف غير مدعوم.
    """
    allowed  = config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "webp"})
    folder   = config.get("UPLOAD_FOLDER", "uploads/images")

    ext = _get_extension(file.filename)
    if not ext or ext.lower() not in allowed:
        return None

    os.makedirs(folder, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}.{ext.lower()}"
    safe_name   = secure_filename(unique_name)
    file_path   = os.path.join(folder, safe_name)
    file.save(file_path)

    return f"/uploads/images/{safe_name}"


def _get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1] if "." in filename else ""


# ── تقسيم النتائج إلى صفحات ───────────────────────────────────────────────────
def paginate_query(query, page: int, per_page: int) -> dict:
    """
    يعيد dict يحتوي على:
      items    → قائمة النتائج في الصفحة الحالية
      total    → إجمالي عدد النتائج
      page     → الصفحة الحالية
      pages    → إجمالي عدد الصفحات
      per_page → عدد النتائج في الصفحة
    """
    page     = max(1, page)
    per_page = max(1, min(per_page, 100))  # حد أقصى 100

    total  = query.count()
    items  = query.offset((page - 1) * per_page).limit(per_page).all()
    pages  = (total + per_page - 1) // per_page if total > 0 else 1

    return {
        "items":    items,
        "total":    total,
        "page":     page,
        "pages":    pages,
        "per_page": per_page,
    }
