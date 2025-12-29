{
    'name': "Dumuc Recruitment Core",
    'summary': "Core hệ thống tuyển dụng Dumuc",
    'version': "1.0",
    'category': "Human Resources",
    'author': "Dumuc",
    'license': "LGPL-3",

    # core dependency only
    'depends': ['base'],

    'data': [
        # security
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',

        
        # 'views/recruit_config_views.xml',

        # demo / seed
        'data/credit_package_data.xml',
        'data/service_plan_data.xml',

        # # views
        # 'views/job_views.xml',
        # 'views/company_views.xml',
        # 'views/seeker_views.xml',
        # 'views/credit_views.xml',
    ],
    "external_dependencies": {"python": ["PyJWT"]},
    # allow demo install optional
    'demo': [
        # optionally load same seed here if needed
    ],

    # module is application
    'application': True,
}
