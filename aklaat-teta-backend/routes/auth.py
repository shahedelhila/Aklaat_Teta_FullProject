"""
مسارات المصادقة - Auth Routes
POST /api/auth/login    → تسجيل دخول الأدمن
POST /api/auth/register → إنشاء حساب أدمن (أول مرة فقط)
GET  /api/auth/me       → بيانات الأدمن الحالي
"""

import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from models import AdminUser
from extensions import db

auth_bp = Blueprint("auth", __name__)


# ── POST /api/auth/login ──────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "البيانات مفقودة"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "اسم المستخدم وكلمة المرور مطلوبان"}), 400

    user = AdminUser.query.filter_by(username=username).first()

    if not user or not bcrypt.checkpw(
        password.encode("utf-8"),
        user.password_hash.encode("utf-8")
    ):
        return jsonify({"error": "اسم المستخدم أو كلمة المرور غلط"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": token,
        "user": user.to_dict(),
        "message": "مرحباً بك في لوحة تحكم تيتا 👋",
    }), 200


# ── POST /api/auth/register ───────────────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    يُسمح بالتسجيل فقط لو ما في أدمن مسجّل بعد
    (لأول إعداد للنظام)
    """
    if AdminUser.query.count() > 0:
        return jsonify({"error": "التسجيل مقفل. تواصل مع المطور."}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "البيانات مفقودة"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or len(username) < 3:
        return jsonify({"error": "اسم المستخدم يجب أن يكون 3 أحرف على الأقل"}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "كلمة المرور يجب أن تكون 6 أحرف على الأقل"}), 400

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user = AdminUser(
        username      = username,
        password_hash = hashed.decode("utf-8"),
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": token,
        "user": user.to_dict(),
        "message": "تم إنشاء حساب الأدمن بنجاح ✅",
    }), 201


# ── GET /api/auth/me ──────────────────────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = AdminUser.query.get(int(user_id))
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404
    return jsonify(user.to_dict()), 200
