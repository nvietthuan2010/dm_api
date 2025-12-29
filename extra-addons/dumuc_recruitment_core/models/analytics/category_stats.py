from odoo import models, fields


class CategoryStats(models.Model):
    _name = "dumuc.category.stats"
    _description = "Thống kê theo ngành nghề / phân loại"

    category_id = fields.Many2one(
        "dumuc.category",
        string="Phân loại ngành nghề"
    )

    total_jobs = fields.Integer(string="Tổng số tin")
    total_applicants = fields.Integer(string="Tổng số ứng viên")
    total_matches = fields.Integer(string="Tổng số matching")
