from odoo import models, fields


class SkillCategory(models.Model):
    _name = "dumuc.skill.category"
    _description = "Nhóm kỹ năng"

    name = fields.Char(
        string="Tên nhóm kỹ năng",
        required=True
    )
    description = fields.Text(string="Mô tả")

    skill_detail_ids = fields.One2many(
        "dumuc.skill.detail",
        "category_id",
        string="Danh sách kỹ năng"
    )
