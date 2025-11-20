{
    'name': "CBU Currency Rate",
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': "O'zbekiston Markaziy Bank valyuta kurslari",
    'description': """
O'zbekiston Markaziy Bank dan avtomatik valyuta kurslarini olish.

Foydalanish:
Settings → Technical → Scheduled Actions → 
"CBU: Update Currency Rates" → Run Manually
    """,
    'author': "Jamoliddin Saydirasulov",
    'website': "https://cbu.uz",
    'depends': ['base', 'account'],
    'data': [
        'data/ir_cron.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}