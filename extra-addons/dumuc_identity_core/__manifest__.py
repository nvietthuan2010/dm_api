# -*- coding: utf-8 -*-
{
    "name": "DuMuc Identity Core",
    "version": "1.0.0",
    "summary": "Centralized identity & role binding platform core for DuMuc ecosystem",
    "category": "Tools",
    "author": "DuMuc Platform",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/identity_groups.xml",
        "security/ir.model.access.csv",

        "views/menu_identity.xml",
        "views/role_binding_views.xml",
        "views/auth_device_views.xml",
        "views/auth_token_views.xml",
        "views/res_users_views.xml",
    ],
    "application": True,
    "installable": True,
}
