# 🤖 بوت تيليجرام مستقل - Mostaql Telegram Bot

بوت تيليجرام يقوم بجمع ومراقبة المشاريع الجديدة من موقع مستقل وإرسالها مباشرة إلى المستخدمين المسجلين.

[![Deploy Telegram Bot](https://github.com/[YOUR_USERNAME]/[REPO_NAME]/actions/workflows/bot-deployment.yml/badge.svg)](https://github.com/[YOUR_USERNAME]/[REPO_NAME]/actions/workflows/bot-deployment.yml)

## 🌟 المميزات

- ✨ جمع المشاريع الجديدة من موقع مستقل تلقائياً
- 📬 إرسال تنبيهات فورية للمشاريع الجديدة
- 📊 مراقبة استخدام موارد النظام (CPU & Memory)
- 🔄 تحديث مستمر للمشاريع
- 🔒 آمن مع إدارة التوكن
- 🚀 نشر تلقائي باستخدام GitHub Actions

## 📋 المتطلبات

- Python 3.9+
- Firefox Browser
- Telegram Bot Token

## 🛠️ التثبيت المحلي

1. استنسخ المستودع:
```bash
git clone https://github.com/[YOUR_USERNAME]/[REPO_NAME].git
cd [REPO_NAME]
```

2. إنشاء بيئة افتراضية:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows
```

3. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

4. إعداد متغيرات البيئة:
```bash
export TELEGRAM_TOKEN='your-telegram-token'  # Linux/Mac
# أو
set TELEGRAM_TOKEN=your-telegram-token  # Windows
```

## 🚀 التشغيل

1. تشغيل البوت محلياً:
```bash
python bot.py
```

2. في تيليجرام:
   - ابدأ محادثة مع البوت
   - أرسل الأمر `/start` للتسجيل
   - استخدم الأمر `/scrape` لجلب المشاريع

## ⚙️ النشر على GitHub Actions

1. انشئ مستودع على GitHub

2. أضف السر `TELEGRAM_TOKEN` في إعدادات GitHub:
   - اذهب إلى `Settings` > `Secrets and variables` > `Actions`
   - انقر على `New repository secret`
   - أضف `TELEGRAM_TOKEN` مع قيمة التوكن الخاص بك

3. ادفع الكود إلى المستودع:
```bash
git push origin main
```

## 📝 أوامر البوت

- `/start` - تسجيل المستخدم لتلقي التنبيهات
- `/scrape` - بدء عملية جمع المشاريع الجديدة

## 🔧 التخصيص

يمكنك تعديل السلوك الافتراضي للبوت من خلال تحديث المتغيرات التالية في `bot.py`:

```python
# عدد المشاريع التي سيتم جمعها
for scrap in range(1, 16):  # تعديل الرقم 16 لتغيير عدد المشاريع

# فترة مراقبة الموارد
await asyncio.sleep(10)  # تعديل الرقم 10 لتغيير فترة المراقبة
```

## 🤝 المساهمة

المساهمات مرحب بها! يمكنك:

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة: `git checkout -b feature/amazing-feature`
3. Commit التغييرات: `git commit -m 'Add amazing feature'`
4. Push إلى الفرع: `git push origin feature/amazing-feature`
5. فتح Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت [MIT License](LICENSE).

## ⚠️ تنبيه

- تأكد من الامتثال لشروط استخدام موقع مستقل
- لا تقم بإجراء طلبات كثيرة في وقت قصير لتجنب الحظر
- احتفظ بتوكن البوت الخاص بك آمناً

## 📧 الدعم

إذا واجهت أي مشاكل أو لديك اقتراحات، يرجى:
- فتح [issue](https://github.com/[YOUR_USERNAME]/[REPO_NAME]/issues)
- أو التواصل عبر [Telegram](https://t.me/[YOUR_TELEGRAM])

## 🌟 شكر خاص

شكر خاص لجميع المساهمين والمكتبات المستخدمة في هذا المشروع:
- [python-telegram-bot](https://python-telegram-bot.org/)
- [Selenium](https://selenium-python.readthedocs.io/)
- [psutil](https://psutil.readthedocs.io/)

---
صنع بـ ❤️ للمجتمع العربي البرمجي
