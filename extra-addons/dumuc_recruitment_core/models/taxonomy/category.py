from odoo import models, fields


class Category(models.Model):
    _name = "dumuc.category"
    _description = "Phân loại ngành nghề"

    industry_id = fields.Many2one(
        "dumuc.industry",
        string="Ngành nghề"
    )

    name = fields.Char(
        string="Tên phân loại",
        required=True
    )
    description = fields.Text(string="Mô tả")

    position_ids = fields.One2many(
        "dumuc.position",
        "category_id",
        string="Danh sách vị trí"
    )
