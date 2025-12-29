from odoo import models, fields

class Skill(models.Model):
    _name = 'dumuc.skill'
    _description = "Kỹ năng"

    name = fields.Char(string="Tên kỹ năng", required=True)
    skill_category_id = fields.Many2one('dumuc.skill.category', string="Nhóm kỹ năng")
    category_id = fields.Many2one('dumuc.job.category', string="Ngành")
