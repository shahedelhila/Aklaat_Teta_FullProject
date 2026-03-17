"""
مسارات التواصل - Contact Routes
POST /api/contact          → إرسال رسالة تواصل
GET  /api/contact/messages → عرض كل الرسائل (Admin)
PUT  /api/contact/<id>/read → تحديد كقُرئ (Admin)
DELETE /api/contact/<id>   → حذف رسالة (Admin)
"""

import re
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from models import ContactMessage
from extensions import db

contact_bp = Blueprint("contact", __name__)


def _is_valid_email(email: str) -> bool:
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))


# ── POST /api/contact ─────────────────────────────────────────────────────────
@contact_bp.route("", methods=["POST"])
def send_message():
    data = request.get_json()
    if not data:
        return jsonify({"error": "البيانات مفقودة"}), 400

    name    = data.get("name", "").strip()
    email   = data.get("email", "").strip()
    message = data.get("message", "").strip()

    # Validation
    errors = {}
    if not name:
        errors["name"] = "الاسم مطلوب"
    if not email or not _is_valid_email(email):
        errors["email"] = "البريد الإلكتروني غير صحيح"
    if not message or len(message) < 10:
        errors["message"] = "الرسالة قصيرة جداً (10 أحرف على الأقل)"
    if len(message) > 2000:
        errors["message"] = "الرسالة طويلة جداً (الحد 2000 حرف)"

    if errors:
        return jsonify({"errors": errors}), 422

    msg = ContactMessage(name=name, email=email, message=message)
    db.session.add(msg)
    db.session.commit()

    # إرسال بريد إلكتروني (اختياري - يعمل لو إعدادات Mail مضبوطة)
    _try_send_email(name, email, message, current_app)

    return jsonify({
        "message": "✅ تم استلام رسالتك! سنرد عليكِ قريباً.",
        "id": msg.id,
    }), 201


# ── GET /api/contact/messages ─────────────────────────────────────────────────
@contact_bp.route("/messages", methods=["GET"])
@jwt_required()
def get_messages():
    show_unread = request.args.get("unread", "false").lower() == "true"
    query = ContactMessage.query
    if show_unread:
        query = query.filter_by(is_read=False)
    messages = query.order_by(ContactMessage.created_at.desc()).all()
    return jsonify([m.to_dict() for m in messages]), 200


# ── PUT /api/contact/<id>/read ────────────────────────────────────────────────
@contact_bp.route("/<int:msg_id>/read", methods=["PUT"])
@jwt_required()
def mark_read(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    return jsonify({"message": "تم التحديد كمقروء"}), 200


# ── DELETE /api/contact/<id> ──────────────────────────────────────────────────
@contact_bp.route("/<int:msg_id>", methods=["DELETE"])
@jwt_required()
def delete_message(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({"message": "تم حذف الرسالة"}), 200


# ── helper: إرسال بريد (صامت لو فاشل) ────────────────────────────────────────
def _try_send_email(name, sender_email, message, app):
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        mail_user = app.config.get("MAIL_USERNAME")
        mail_pass = app.config.get("MAIL_PASSWORD")
        recipient = app.config.get("MAIL_RECIPIENT")

        if not mail_user or not mail_pass:
            return  # لم يتم إعداد SMTP

        msg = MIMEMultipart()
        msg["From"]    = mail_user
        msg["To"]      = recipient
        msg["Subject"] = f"رسالة جديدة من {name} - أكلات تيتا"

        body = f"""
رسالة جديدة وصلت لموقع أكلات تيتا:

الاسم: {name}
البريد: {sender_email}

الرسالة:
{message}
        """
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(app.config["MAIL_SERVER"],
                          app.config["MAIL_PORT"]) as server:
            server.starttls()
            server.login(mail_user, mail_pass)
            server.send_message(msg)
    except Exception:
        pass  # فشل البريد لا يوقف الـ API
