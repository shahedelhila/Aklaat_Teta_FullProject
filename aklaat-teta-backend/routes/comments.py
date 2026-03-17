"""
مسارات التعليقات - Comments Routes
GET  /api/comments/<recipe_id>      → تعليقات وصفة (المعتمدة فقط)
POST /api/comments/<recipe_id>      → إضافة تعليق جديد
GET  /api/comments/pending          → التعليقات المنتظرة الموافقة (Admin)
PUT  /api/comments/<id>/approve     → اعتماد تعليق (Admin)
DELETE /api/comments/<id>           → حذف تعليق (Admin)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Comment, Recipe
from extensions import db

comments_bp = Blueprint("comments", __name__)


# ── GET /api/comments/<recipe_id> ─────────────────────────────────────────────
@comments_bp.route("/<string:recipe_id>", methods=["GET"])
def get_comments(recipe_id):
    Recipe.query.get_or_404(recipe_id, description="الوصفة غير موجودة")

    comments = Comment.query.filter_by(
        recipe_id=recipe_id, is_approved=True
    ).order_by(Comment.created_at.desc()).all()

    return jsonify([c.to_dict() for c in comments]), 200


# ── POST /api/comments/<recipe_id> ────────────────────────────────────────────
@comments_bp.route("/<string:recipe_id>", methods=["POST"])
def add_comment(recipe_id):
    Recipe.query.get_or_404(recipe_id, description="الوصفة غير موجودة")

    data = request.get_json()
    if not data:
        return jsonify({"error": "البيانات مفقودة"}), 400

    author = data.get("author_name", "").strip()
    text   = data.get("text", "").strip()

    if not author or not text:
        return jsonify({"error": "الاسم والتعليق مطلوبان"}), 400

    if len(text) > 1000:
        return jsonify({"error": "التعليق طويل جداً (الحد 1000 حرف)"}), 400

    comment = Comment(
        recipe_id   = recipe_id,
        author_name = author,
        text        = text,
        is_approved = False,   # ينتظر موافقة الأدمن
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "message": "شكراً لتعليقك! سيظهر بعد مراجعة تيتا 😊",
        "comment": comment.to_dict(),
    }), 201


# ── GET /api/comments/pending ─────────────────────────────────────────────────
@comments_bp.route("/pending", methods=["GET"])
@jwt_required()
def get_pending_comments():
    comments = Comment.query.filter_by(is_approved=False)\
                            .order_by(Comment.created_at.asc()).all()
    return jsonify([c.to_dict() for c in comments]), 200


# ── PUT /api/comments/<id>/approve ────────────────────────────────────────────
@comments_bp.route("/<int:comment_id>/approve", methods=["PUT"])
@jwt_required()
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.is_approved = True
    db.session.commit()
    return jsonify({"message": "تم اعتماد التعليق", "comment": comment.to_dict()}), 200


# ── DELETE /api/comments/<id> ─────────────────────────────────────────────────
@comments_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "تم حذف التعليق"}), 200
