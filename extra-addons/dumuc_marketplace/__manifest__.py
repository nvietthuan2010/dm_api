# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "DuMuc Marketplace Core",
    'version' : '1.0',
    "summary": "Core listing & vehicle models for DuMuc.net",
    "author": "DuMuc",
    "depends": [
        "base",
        "mail",      # để dùng chatter
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizard/wizard_reject_views.xml",
        "wizard/wizard_boost_views.xml",
        "views/vehicle_views.xml",
        "views/listing_views.xml",
        "views/evaluator_views.xml",
        "views/evaluator_review_views.xml",
        "views/violation_views.xml",
        "views/inspection_views.xml",
        "views/service_package_views.xml",
        "views/menu.xml",

    ],
    "application": True,
}
