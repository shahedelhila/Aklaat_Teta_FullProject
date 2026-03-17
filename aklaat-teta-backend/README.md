# أكلات تيتا — Backend API 🫙

باك إيند كامل لموقع الوصفات الفلسطينية التراثية.  
**تقنيات:** Python · Flask · SQLite · JWT

---

## 🚀 تشغيل المشروع

```bash
# 1. تثبيت المتطلبات
pip install -r requirements.txt

# 2. إعداد ملف البيئة
cp .env.example .env
# عدّل القيم في .env

# 3. تشغيل السيرفر
python app.py
```

السيرفر يشتغل على: `http://localhost:5000`

---

## 📁 هيكل المشروع

```
aklaat-teta-backend/
├── app.py                  ← نقطة التشغيل
├── config.py               ← كل الإعدادات
├── extensions.py           ← SQLAlchemy + JWT
├── models.py               ← نماذج DB
├── requirements.txt
├── .env.example
├── routes/
│   ├── recipes.py          ← CRUD الوصفات
│   ├── comments.py         ← التعليقات
│   ├── contact.py          ← رسائل التواصل
│   ├── favorites.py        ← المفضلة
│   ├── auth.py             ← تسجيل دخول الأدمن
│   └── admin.py            ← لوحة التحكم
└── utils/
    ├── helpers.py          ← رفع الصور + الصفحات
    └── seeder.py           ← بذار بيانات الوصفات
```

---

## 📡 كل الـ Endpoints

### 🥘 الوصفات `/api/recipes`

| Method | Endpoint | الوصف | Auth |
|--------|----------|-------|------|
| GET | `/api/recipes` | كل الوصفات (فلترة + بحث + صفحات) | — |
| GET | `/api/recipes/featured` | الوصفات المميزة | — |
| GET | `/api/recipes/categories` | قائمة التصنيفات | — |
| GET | `/api/recipes/<id>` | وصفة كاملة بالمكونات والخطوات | — |
| POST | `/api/recipes` | إضافة وصفة | ✅ Admin |
| PUT | `/api/recipes/<id>` | تعديل وصفة | ✅ Admin |
| DELETE | `/api/recipes/<id>` | حذف وصفة | ✅ Admin |
| POST | `/api/recipes/<id>/image` | رفع صورة | ✅ Admin |

**Query params للبحث والفلترة:**
```
GET /api/recipes?category=main&search=مسخن&page=1&per_page=12
```

---

### 💬 التعليقات `/api/comments`

| Method | Endpoint | الوصف | Auth |
|--------|----------|-------|------|
| GET | `/api/comments/<recipe_id>` | تعليقات وصفة (المعتمدة) | — |
| POST | `/api/comments/<recipe_id>` | إضافة تعليق | — |
| GET | `/api/comments/pending` | التعليقات المنتظرة | ✅ Admin |
| PUT | `/api/comments/<id>/approve` | اعتماد تعليق | ✅ Admin |
| DELETE | `/api/comments/<id>` | حذف تعليق | ✅ Admin |

**Body لإضافة تعليق:**
```json
{
  "author_name": "أم محمد",
  "text": "جربت المسخن وطلع رائع!"
}
```

---

### 📬 التواصل `/api/contact`

| Method | Endpoint | الوصف | Auth |
|--------|----------|-------|------|
| POST | `/api/contact` | إرسال رسالة | — |
| GET | `/api/contact/messages` | كل الرسائل | ✅ Admin |
| PUT | `/api/contact/<id>/read` | تحديد كمقروء | ✅ Admin |
| DELETE | `/api/contact/<id>` | حذف رسالة | ✅ Admin |

**Body لإرسال رسالة:**
```json
{
  "name": "سارة",
  "email": "sara@example.com",
  "message": "أريد مشاركة وصفة ستي!"
}
```

---

### ❤️ المفضلة `/api/favorites`

| Method | Endpoint | الوصف |
|--------|----------|-------|
| POST | `/api/favorites/validate` | التحقق من IDs المحفوظة |
| GET | `/api/favorites/<ids>` | جلب وصفات بـ IDs مفصولة بفاصلة |

**مثال:**
```
GET /api/favorites/musakhan,kaak,humos
```

```json
POST /api/favorites/validate
{ "ids": ["musakhan", "kaak", "deleted-recipe"] }
```

---

### 🔐 المصادقة `/api/auth`

| Method | Endpoint | الوصف |
|--------|----------|-------|
| POST | `/api/auth/register` | إنشاء حساب أدمن (مرة واحدة) |
| POST | `/api/auth/login` | تسجيل دخول |
| GET | `/api/auth/me` | بيانات الأدمن الحالي |

**تسجيل الدخول:**
```json
POST /api/auth/login
{ "username": "admin", "password": "yourpassword" }
```

**استخدام التوكن:**
```
Authorization: Bearer <access_token>
```

---

### 📊 لوحة التحكم `/api/admin`

| Method | Endpoint | الوصف | Auth |
|--------|----------|-------|------|
| GET | `/api/admin/stats` | إحصائيات عامة | ✅ Admin |
| GET | `/api/admin/comments` | كل التعليقات | ✅ Admin |
| GET | `/api/admin/messages` | الرسائل غير المقروءة | ✅ Admin |

---

## 🔌 ربط الفرونت إيند

### استبدال localStorage بالـ API

```javascript
// بدلاً من localStorage للمفضلة
const API = "http://localhost:5000/api";

// جلب وصفة
const recipe = await fetch(`${API}/recipes/musakhan`).then(r => r.json());

// التحقق من المفضلة
const savedIds = JSON.parse(localStorage.getItem("myFavorites")) || [];
const res = await fetch(`${API}/favorites/validate`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ ids: savedIds }),
});
const { recipes, valid_ids } = await res.json();

// إرسال رسالة تواصل
await fetch(`${API}/contact`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name, email, message }),
});

// إضافة تعليق
await fetch(`${API}/comments/musakhan`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ author_name: "أم محمد", text: "رائع!" }),
});
```

---

## 🗄️ نماذج قاعدة البيانات

```
Recipe          → id, title, category, image, story, prep_time, difficulty, is_featured
Ingredient      → id, recipe_id, text, order
Step            → id, recipe_id, text, order
Comment         → id, recipe_id, author_name, text, is_approved, created_at
ContactMessage  → id, name, email, message, is_read, created_at
AdminUser       → id, username, password_hash, created_at
```

---

## ☁️ النشر على Render (مجاني)

```bash
# أضف هذا الملف: Procfile
web: python app.py

# أو gunicorn للإنتاج
web: gunicorn app:create_app()
```

---

*صُنع بالحب لتيتا وكل جداتنا الفلسطينيات 🫒*
