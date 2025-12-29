from odoo import models, fields


class Position(models.Model):
    _name = "dumuc.position"
    _description = "Vị trí công việc"

    category_id = fields.Many2one(
        "dumuc.category",
        string="Phân loại"
    )

    name = fields.Char(
        string="Tên vị trí",
        required=True
    )

    description = fields.Text(string="Mô tả vị trí")
