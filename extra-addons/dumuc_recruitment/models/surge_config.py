from odoo import models, fields


class SurgeConfig(models.Model):
    _name = "dumuc.surge.config"
    _description = "Cấu hình dynamic pricing"

    enable_surge = fields.Boolean("Bật Dynamic Pricing", default=False)

    peak_start = fields.Float("Giờ bắt đầu cao điểm", default=17.0)   # 17:00
    peak_end = fields.Float("Giờ kết thúc cao điểm", default=20.0)     # 20:00
    peak_multiplier = fields.Float("Hệ số giờ cao điểm", default=1.2)

    distance_threshold_km = fields.Float("Ngưỡng khoảng cách (km)", default=10.0)
    distance_multiplier = fields.Float("Hệ số khoảng cách xa", default=1.15)

    urgent_multiplier = fields.Float("Hệ số khẩn cấp", default=1.25)

    rating_threshold = fields.Float("Ngưỡng rating cao", default=4.8)
    rating_multiplier = fields.Float("Hệ số rating cao", default=1.1)

    supply_demand_multiplier = fields.Float("Hệ số cung-cầu", default=1.3)
