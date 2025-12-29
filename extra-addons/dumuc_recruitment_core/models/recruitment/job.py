from odoo import models, fields, api
from datetime import timedelta


class Job(models.Model):
    _inherit = "hr.job"
    _description = "Tin tuyển dụng"

    job_code = fields.Char(
        string="Mã tin tuyển dụng",
        required=True,
        help="Mã định danh duy nhất của tin tuyển dụng"
    )

    visibility = fields.Selection([
        ('public', 'Công khai'),
        ('private', 'Riêng tư')
    ], string="Chế độ hiển thị", default="public")

    premium = fields.Boolean(
        string="Tin gấp / tin ưu tiên",
        default=False
    )

    post_date = fields.Date(string="Ngày đăng")
    expire_date = fields.Date(string="Ngày hết hạn")
    duration_days = fields.Integer(
        string="Số ngày hiệu lực đăng tin",
        default=30
    )

    approval_state = fields.Selection([
        ('draft', 'Nháp'),
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('published', 'Đã đăng'),
        ('expired', 'Hết hạn')
    ], string="Trạng thái duyệt", default='draft')

    screening_question_ids = fields.One2many(
        "dumuc.screening.question",
        "job_id",
        string="Danh sách câu hỏi sàng lọc"
    )

    scoring_rule_ids = fields.One2many(
        "dumuc.scoring.rule",
        "job_id",
        string="Quy tắc tính điểm"
    )

    matching_score = fields.Float(
        string="Điểm matching trung bình",
        compute="_compute_matching_score"
    )

    garage_id = fields.Many2one(
        "dumuc.garage.profile",
        string="Garage / nhà tuyển dụng"
    )

    def action_submit(self):
        """Nhà tuyển dụng gửi tin để moderator duyệt"""
        for job in self:
            job.approval_state = 'pending'
            self.env["dumuc.job.approval"].create({
                "job_id": job.id,
                "state": "pending"
            })

    def action_approve(self):
        """Moderator duyệt tin"""
        for job in self:
            job.approval_state = 'approved'
            job.post_date = fields.Date.today()
            job.expire_date = fields.Date.today() + timedelta(days=job.duration_days)
            job.approval_state = 'published'

    def action_reject(self, note=""):
        """Moderator từ chối tin"""
        for job in self:
            job.approval_state = 'rejected'
            self.env["dumuc.job.approval"].create({
                "job_id": job.id,
                "state": "rejected",
                "note": note
            })

    def action_force_expire(self):
        """Moderator chủ động hết hạn tin"""
        for job in self:
            job.approval_state = 'expired'
            job.premium = False

    @api.model
    def cron_auto_expire(self):
        """Cron tự động hết hạn tin đến ngày"""
        today = fields.Date.today()
        expired = self.search([
            ('approval_state', '=', 'published'),
            ('expire_date', '<', today)
        ])
        expired.write({'approval_state': 'expired', 'premium': False})
    
    def action_publish(self):
        self.ensure_one()
        service = self.env.ref("service_post_job")
        wallet = self.env["dumuc.credit.wallet"].get_wallet(self.garage_id)

        wallet.deduct(service.cost, ref=self.id, ref_type="job_post")

        self.approval_state = "published"

