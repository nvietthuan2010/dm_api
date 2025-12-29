from odoo import models, fields

class SeekerExperience(models.Model):
    _name = 'dumuc.seeker.experience'
    _description = "Kinh nghiệm ứng viên"

    seeker_id = fields.Many2one('dumuc.seeker', string="Ứng viên")
    company_name = fields.Char(string="Tên công ty")
    job_title = fields.Char(string="Vị trí")
    start_date = fields.Date(string="Bắt đầu")
    end_date = fields.Date(string="Kết thúc")
    description = fields.Text(string="Mô tả")
