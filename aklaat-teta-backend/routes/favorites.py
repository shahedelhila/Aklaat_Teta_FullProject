"""
مسارات المفضلة - Favorites Routes
(حل سيرفر-سايد للمفضلة بدلاً من localStorage فقط)

POST /api/favorites/validate    → التحقق من أن قائمة IDs صحيحة وإرجاع بيانات الوصفات
GET  /api/favorites/<ids>       → جلب وصفات متعددة بـ IDs (مفصولة بفاصلة)
"""

from flask import Blueprint, request, jsonify
from models import Recipe

favorites_bp = Blueprint("favorites", __name__)


# ── POST /api/favorites/validate ─────────────────────────────────────────────
@favorites_bp.route("/validate", methods=["POST"])
def validate_favorites():
    """
    يستقبل قائمة من IDs المحفوظة في localStorage
    ويعيد بيانات الوصفات الموجودة فعلاً في الـ DB
    مفيد لو الوصفة اتحذفت من السيرفر
    """
    data = request.get_json()
    if not data or "ids" not in data:
        return jsonify({"error": "مطلوب حقل 'ids'"}), 400

    ids = data["ids"]
    if not isinstance(ids, list):
        return jsonify({"error": "'ids' يجب أن يكون مصفوفة"}), 400

    # جلب الوصفات الموجودة فقط
    recipes = Recipe.query.filter(Recipe.id.in_(ids)).all()
    found_ids = {r.id for r in recipes}

    return jsonify({
        "recipes":     [r.to_dict() for r in recipes],
        "valid_ids":   list(found_ids),
        "invalid_ids": [rid for rid in ids if rid not in found_ids],
    }), 200


# ── GET /api/favorites/<ids> ──────────────────────────────────────────────────
@favorites_bp.route("/<string:ids_str>", methods=["GET"])
def get_favorites_by_ids(ids_str):
    """
    مثال: GET /api/favorites/musakhan,kaak,humos
    """
    ids = [i.strip() for i in ids_str.split(",") if i.strip()]
    if not ids:
        return jsonify([]), 200

    recipes = Recipe.query.filter(Recipe.id.in_(ids)).all()
    return jsonify([r.to_dict() for r in recipes]), 200
