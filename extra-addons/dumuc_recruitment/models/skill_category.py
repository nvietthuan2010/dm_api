from odoo import models, fields

class SkillCategory(models.Model):
    _name = 'dumuc.skill.category'
    _description = "Nhóm kỹ năng"

    name = fields.Char(string="Tên nhóm", required=True)
    category_id = fields.Many2one('dumuc.job.category', string="Ngành liên quan")
    skill_ids = fields.One2many('dumuc.skill', 'skill_category_id', string="Kỹ năng")
