from odoo import models, fields


class Industry(models.Model):
    _name = "dumuc.industry"
    _description = "Ngành nghề"

    name = fields.Char(
        string="Tên ngành",
        required=True
    )
    description = fields.Text(string="Mô tả ngành")

    category_ids = fields.One2many(
        "dumuc.category",
        "industry_id",
        string="Danh sách phân loại"
    )
