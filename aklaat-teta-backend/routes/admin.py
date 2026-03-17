"""
مسارات لوحة التحكم - Admin Routes
GET  /api/admin/stats          → إحصائيات عامة
GET  /api/admin/comments       → كل التعليقات (معتمدة وغير معتمدة)
GET  /api/admin/messages       → رسائل التواصل غير المقروءة
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import Recipe, Comment, ContactMessage
from extensions import db

admin_bp = Blueprint("admin", __name__)


# ── GET /api/admin/stats ──────────────────────────────────────────────────────
@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    total_recipes      = Recipe.query.count()
    featured_recipes   = Recipe.query.filter_by(is_featured=True).count()
    total_comments     = Comment.query.count()
    pending_comments   = Comment.query.filter_by(is_approved=False).count()
    total_messages     = ContactMessage.query.count()
    unread_messages    = ContactMessage.query.filter_by(is_read=False).count()

    by_category = {}
    for cat in ["main", "side", "sweet"]:
        by_category[cat] = Recipe.query.filter_by(category=cat).count()

    return jsonify({
        "recipes": {
            "total":    total_recipes,
            "featured": featured_recipes,
            "by_category": by_category,
        },
        "comments": {
            "total":   total_comments,
            "pending": pending_comments,
        },
        "messages": {
            "total":  total_messages,
            "unread": unread_messages,
        },
    }), 200


# ── GET /api/admin/comments ───────────────────────────────────────────────────
@admin_bp.route("/comments", methods=["GET"])
@jwt_required()
def get_all_comments():
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return jsonify([c.to_dict() for c in comments]), 200


# ── GET /api/admin/messages ───────────────────────────────────────────────────
@admin_bp.route("/messages", methods=["GET"])
@jwt_required()
def get_unread_messages():
    messages = ContactMessage.query.filter_by(is_read=False)\
                                   .order_by(ContactMessage.created_at.desc()).all()
    return jsonify([m.to_dict() for m in messages]), 200
