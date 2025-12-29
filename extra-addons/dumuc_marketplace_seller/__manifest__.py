{
    'name': 'DuMuc Marketplace Seller',
    'version': '1.0.0',
    'summary': 'DuMuc Marketplace Seller Tools',
    'description': """
        Seller dashboard, inspection overview, finance overview
        for DuMuc marketplace system.
    """,
    'category': 'Tools',
    'author': 'DuMuc',
    'depends': [
        'web',
        'dumuc_marketplace',
    ],
    'data': [
        'views/seller_view.xml',
        'views/seller_action.xml',
        'views/menu.xml',
    ],
    
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
