{
    'name': 'DuMuc Marketplace Admin',
    'version': '1.0.0',
    'summary': 'DuMuc Marketplace Admin Dashboard & Moderation Tools',
    'description': """
        Admin dashboard, moderation, inspection overview, finance overview
        for DuMuc marketplace system.
    """,
    'category': 'Tools',
    'author': 'DuMuc',
    'depends': [
        'web',
        'dumuc_marketplace',
    ],
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/moderation_list_views.xml',
        'views/user_view.xml',
        'views/admin_dashboard_views.xml',
        'data/admin_cron.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dumuc_marketplace_admin/static/src/js/admin_dashboard.js',
            'dumuc_marketplace_admin/static/src/xml/admin_dashboard_templates.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
