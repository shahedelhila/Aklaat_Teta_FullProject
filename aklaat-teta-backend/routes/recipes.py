"""
مسارات الوصفات - Recipes Routes
GET  /api/recipes                  → كل الوصفات (مع فلترة وبحث وصفحات)
GET  /api/recipes/featured         → الوصفات المميزة
GET  /api/recipes/categories       → قائمة التصنيفات
GET  /api/recipes/<id>             → وصفة محددة بالتفاصيل الكاملة
POST /api/recipes                  → إضافة وصفة جديدة (Admin)
PUT  /api/recipes/<id>             → تعديل وصفة (Admin)
DELETE /api/recipes/<id>           → حذف وصفة (Admin)
POST /api/recipes/<id>/image       → رفع صورة للوصفة (Admin)
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from models import Recipe, Ingredient, Step
from extensions import db
from utils.helpers import save_image, paginate_query

recipes_bp = Blueprint("recipes", __name__)


# ── GET /api/recipes ─────────────────────────────────────────────────────────
@recipes_bp.route("", methods=["GET"])
def get_recipes():
    """
    Query params:
      category  → main | side | sweet | all
      search    → نص البحث في العنوان
      page      → رقم الصفحة (default 1)
      per_page  → عدد النتائج (default 12)
    """
    category = request.args.get("category", "all")
    search   = request.args.get("search", "").strip()
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page",
                   current_app.config.get("RECIPES_PER_PAGE", 12)))

    query = Recipe.query

    if category and category != "all":
        query = query.filter_by(category=category)

    if search:
        query = query.filter(Recipe.title.ilike(f"%{search}%"))

    query = query.order_by(Recipe.is_featured.desc(), Recipe.created_at.desc())

    result = paginate_query(query, page, per_page)

    return jsonify({
        "recipes":    [r.to_dict() for r in result["items"]],
        "total":      result["total"],
        "page":       result["page"],
        "pages":      result["pages"],
        "per_page":   result["per_page"],
    }), 200


# ── GET /api/recipes/featured ────────────────────────────────────────────────
@recipes_bp.route("/featured", methods=["GET"])
def get_featured():
    limit = int(request.args.get("limit", 3))
    recipes = Recipe.query.filter_by(is_featured=True)\
                          .order_by(Recipe.created_at.desc())\
                          .limit(limit).all()
    return jsonify([r.to_dict() for r in recipes]), 200


# ── GET /api/recipes/categories ──────────────────────────────────────────────
@recipes_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = [
        {"id": "main",  "label": "أطباق رئيسية"},
        {"id": "side",  "label": "مقبلات"},
        {"id": "sweet", "label": "حلويات"},
    ]
    return jsonify(categories), 200


# ── GET /api/recipes/<id> ─────────────────────────────────────────────────────
@recipes_bp.route("/<string:recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id,
                                     description="الوصفة غير موجودة")
    return jsonify(recipe.to_dict(full=True)), 200


# ── POST /api/recipes ─────────────────────────────────────────────────────────
@recipes_bp.route("", methods=["POST"])
@jwt_required()
def create_recipe():
    data = request.get_json()

    if not data:
        return jsonify({"error": "البيانات مفقودة"}), 400

    required = ["id", "title", "category"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"الحقل '{field}' مطلوب"}), 400

    if Recipe.query.get(data["id"]):
        return jsonify({"error": "معرّف الوصفة موجود مسبقاً"}), 409

    recipe = Recipe(
        id          = data["id"].strip(),
        title       = data["title"].strip(),
        category    = data["category"],
        story       = data.get("story", ""),
        image       = data.get("image", ""),
        prep_time   = data.get("prep_time"),
        difficulty  = data.get("difficulty", "متوسطة"),
        is_featured = data.get("is_featured", False),
    )

    db.session.add(recipe)

    # مكونات
    for idx, ing_text in enumerate(data.get("ingredients", [])):
        db.session.add(Ingredient(recipe_id=recipe.id,
                                  text=ing_text.strip(), order=idx))

    # خطوات
    for idx, step_text in enumerate(data.get("steps", [])):
        db.session.add(Step(recipe_id=recipe.id,
                            text=step_text.strip(), order=idx))

    db.session.commit()
    return jsonify(recipe.to_dict(full=True)), 201


# ── PUT /api/recipes/<id> ─────────────────────────────────────────────────────
@recipes_bp.route("/<string:recipe_id>", methods=["PUT"])
@jwt_required()
def update_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    data   = request.get_json()

    if not data:
        return jsonify({"error": "البيانات مفقودة"}), 400

    # تحديث الحقول الأساسية
    for field in ["title", "category", "story", "image",
                  "prep_time", "difficulty", "is_featured"]:
        if field in data:
            setattr(recipe, field, data[field])

    # تحديث المكونات
    if "ingredients" in data:
        Ingredient.query.filter_by(recipe_id=recipe_id).delete()
        for idx, ing_text in enumerate(data["ingredients"]):
            db.session.add(Ingredient(recipe_id=recipe_id,
                                      text=ing_text.strip(), order=idx))

    # تحديث الخطوات
    if "steps" in data:
        Step.query.filter_by(recipe_id=recipe_id).delete()
        for idx, step_text in enumerate(data["steps"]):
            db.session.add(Step(recipe_id=recipe_id,
                                text=step_text.strip(), order=idx))

    db.session.commit()
    return jsonify(recipe.to_dict(full=True)), 200


# ── DELETE /api/recipes/<id> ──────────────────────────────────────────────────
@recipes_bp.route("/<string:recipe_id>", methods=["DELETE"])
@jwt_required()
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({"message": f"تم حذف الوصفة '{recipe.title}' بنجاح"}), 200


# ── POST /api/recipes/<id>/image ──────────────────────────────────────────────
@recipes_bp.route("/<string:recipe_id>/image", methods=["POST"])
@jwt_required()
def upload_recipe_image(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    if "image" not in request.files:
        return jsonify({"error": "لم يتم إرفاق صورة"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "اسم الملف فارغ"}), 400

    image_url = save_image(file, current_app.config)
    if not image_url:
        return jsonify({"error": "نوع الملف غير مدعوم"}), 415

    recipe.image = image_url
    db.session.commit()

    return jsonify({"image_url": image_url, "message": "تم رفع الصورة بنجاح"}), 200
