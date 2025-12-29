{
    "name": "Du Muc Recruitment Core",
    "summary": "Hệ thống tuyển dụng core: nhà tuyển dụng, ứng viên, tín dụng, taxonomy, kiểm duyệt và analytics.",
    "version": "1.0.0",
    "author": "Du Muc Technology",
    "website": "https://dumuc.vn",
    "license": "LGPL-3",
    "category": "Human Resources / Recruitment",
    "description": """
Core Tuyển Dụng Du Muc
=======================
Module core dùng để:
- quản lý tin tuyển dụng
- quản lý garage / nhà tuyển dụng
- quản lý ứng viên & hồ sơ
- quản lý ví tín dụng & gói dịch vụ
- taxonomy ngành nghề & kỹ năng
- kiểm duyệt & logs
- analytics & reporting

Tích hợp API FE (Next.js) & Odoo Backend.
    """,
    
    "depends": [
        "base",
        "hr",
        "mail",
        "web",
    ],

    "data": [
        # SECURITY
        "security/security.xml",
        "security/ir.model.access.csv",

        # CRON
        "data/cron.xml",

        # SEED DATA
        "data/default_roles.xml",
        "data/default_stages.xml",
        "data/default_credit_services.xml",
        "data/default_categories.xml",
        "data/default_skills.xml",

        # MENUS + VIEWS (phần này build sau)
        # "views/menus.xml",
        # "views/job_views.xml",
        # "views/employer_views.xml",
        # "views/credit_views.xml",
        # "views/taxonomy_views.xml",
        # "views/candidate_views.xml",
        # "views/governance_views.xml",
        # "views/analytics_views.xml",
    ],

    "installable": True,
    "application": True,
    "auto_install": False,
}
