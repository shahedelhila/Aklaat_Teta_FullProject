"""
نماذج قاعدة البيانات لمشروع أكلات تيتا
"""

from datetime import datetime
from extensions import db


# ──────────────────────────────────────────────
#  وصفة Recipe
# ──────────────────────────────────────────────
class Recipe(db.Model):
    __tablename__ = "recipes"

    id          = db.Column(db.String(50),  primary_key=True)   # slug مثل "musakhan"
    title       = db.Column(db.String(200), nullable=False)
    category    = db.Column(db.String(50),  nullable=False)     # main / side / sweet
    image       = db.Column(db.String(300), nullable=True)
    story       = db.Column(db.Text,        nullable=True)
    prep_time   = db.Column(db.Integer,     nullable=True)      # بالدقائق
    difficulty  = db.Column(db.String(50),  nullable=True)      # سهلة / متوسطة / صعبة
    is_featured = db.Column(db.Boolean,     default=False)
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    # علاقات
    ingredients = db.relationship("Ingredient", backref="recipe",
                                  cascade="all, delete-orphan", lazy=True)
    steps       = db.relationship("Step",       backref="recipe",
                                  cascade="all, delete-orphan", lazy=True,
                                  order_by="Step.order")
    comments    = db.relationship("Comment",    backref="recipe",
                                  cascade="all, delete-orphan", lazy=True)

    def to_dict(self, full=False):
        data = {
            "id":         self.id,
            "title":      self.title,
            "category":   self.category,
            "image":      self.image,
            "story":      self.story,
            "prep_time":  self.prep_time,
            "difficulty": self.difficulty,
            "is_featured": self.is_featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if full:
            data["ingredients"] = [i.to_dict() for i in self.ingredients]
            data["steps"]       = [s.to_dict() for s in self.steps]
            data["comments"]    = [
                c.to_dict() for c in self.comments if c.is_approved
            ]
        return data


# ──────────────────────────────────────────────
#  مكوّن Ingredient
# ──────────────────────────────────────────────
class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id        = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.String(50),  db.ForeignKey("recipes.id"), nullable=False)
    text      = db.Column(db.String(500), nullable=False)
    order     = db.Column(db.Integer,     default=0)

    def to_dict(self):
        return {"id": self.id, "text": self.text, "order": self.order}


# ──────────────────────────────────────────────
#  خطوة Step
# ──────────────────────────────────────────────
class Step(db.Model):
    __tablename__ = "steps"

    id        = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.String(50),  db.ForeignKey("recipes.id"), nullable=False)
    text      = db.Column(db.Text,        nullable=False)
    order     = db.Column(db.Integer,     default=0)

    def to_dict(self):
        return {"id": self.id, "text": self.text, "order": self.order}


# ──────────────────────────────────────────────
#  تعليق Comment
# ──────────────────────────────────────────────
class Comment(db.Model):
    __tablename__ = "comments"

    id          = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    recipe_id   = db.Column(db.String(50),  db.ForeignKey("recipes.id"), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    text        = db.Column(db.Text,        nullable=False)
    is_approved = db.Column(db.Boolean,     default=False)   # يحتاج موافقة الأدمن
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":          self.id,
            "recipe_id":   self.recipe_id,
            "author_name": self.author_name,
            "text":        self.text,
            "is_approved": self.is_approved,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }


# ──────────────────────────────────────────────
#  رسالة تواصل ContactMessage
# ──────────────────────────────────────────────
class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id         = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(200), nullable=False)
    message    = db.Column(db.Text,        nullable=False)
    is_read    = db.Column(db.Boolean,     default=False)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "name":       self.name,
            "email":      self.email,
            "message":    self.message,
            "is_read":    self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ──────────────────────────────────────────────
#  مستخدم Admin
# ──────────────────────────────────────────────
class AdminUser(db.Model):
    __tablename__ = "admin_users"

    id           = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    username     = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at   = db.Column(db.DateTime,    default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "username": self.username}
