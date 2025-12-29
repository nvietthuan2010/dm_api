from odoo import models, fields, api, _
from odoo.exceptions import UserError

class JobApplication(models.Model):
    _name = 'dumuc.job.application'
    _description = "Ứng tuyển"

    job_id = fields.Many2one('dumuc.job', string="Tin tuyển dụng")
    seeker_id = fields.Many2one('dumuc.seeker', string="Ứng viên")

    cover_letter = fields.Text(string="Thư tự giới thiệu")

    status = fields.Selection([
        ('new', "Mới"),
        ('viewed', "Đã xem"),
        ('interview', "Phỏng vấn"),
        ('rejected', "Từ chối"),
        ('accepted', "Nhận việc"),
    ], default='new', string="Trạng thái")

    applied_at = fields.Datetime(string="Ngày ứng tuyển", default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        job = self.env['dumuc.job'].browse(vals.get('job_id'))
        seeker = self.env['dumuc.seeker'].browse(vals.get('seeker_id'))
        
        exists = self.search_count([
            ('job_id', '=', job.id),
            ('seeker_id', '=', seeker.id)
        ])

        if exists:
            raise UserError("Bạn đã ứng tuyển tin này.")

        if job.status != 'active':
            raise UserError("Tin không còn nhận ứng tuyển.")

        return super().create(vals)
    
    def mark_viewed(self):
        self.status = 'viewed'

