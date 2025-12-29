from odoo import models, fields


class RecruitConfig(models.Model):
    _name = "dumuc.recruit.config"
    _description = "Cấu hình hệ thống tuyển dụng"

    google_api_key = fields.Char("Google Maps API Key")

    geo_mode = fields.Selection([
        ('disabled', 'Không sử dụng'),
        ('line', 'Haversine'),
        ('drive_google', 'Google Driving'),
        ('drive_osrm', 'OSRM Driving')
    ], default='line', string="Chế độ tính khoảng cách")

    osrm_url = fields.Char(
        "OSRM Server URL",
        default="https://router.project-osrm.org/route/v1"
    )

    geo_cache_expire_days = fields.Integer(
        default=30,
        string="Thời gian cache (ngày)"
    )
