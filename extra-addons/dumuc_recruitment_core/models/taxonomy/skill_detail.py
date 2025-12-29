from odoo import models, fields


class SkillDetail(models.Model):
    _name = "dumuc.skill.detail"
    _description = "Kỹ năng chi tiết"

    category_id = fields.Many2one(
        "dumuc.skill.category",
        string="Nhóm kỹ năng"
    )

    name = fields.Char(
        string="Tên kỹ năng",
        required=True
    )
    description = fields.Text(string="Mô tả kỹ năng")

    tag_ids = fields.Many2many(
        "dumuc.skill.tag",
        string="Thẻ kỹ năng"
    )
