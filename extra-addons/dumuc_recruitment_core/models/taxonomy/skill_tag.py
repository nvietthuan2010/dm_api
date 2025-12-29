from odoo import models, fields


class SkillTag(models.Model):
    _name = "dumuc.skill.tag"
    _description = "Thẻ kỹ năng"

    name = fields.Char(
        string="Tên thẻ",
        required=True
    )
