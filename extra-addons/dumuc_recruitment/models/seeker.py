from odoo import models, fields
from odoo.exceptions import UserError


class JobSeeker(models.Model):
    _name = 'dumuc.seeker'
    _description = "Ứng viên"

    full_name = fields.Char(string="Họ tên", required=True)
    email = fields.Char(string="Email")
    phone = fields.Char(string="Số điện thoại")

    user_id = fields.Many2one('res.users', string="Tài khoản")
    category_id = fields.Many2one('dumuc.job.category', string="Ngành")
    exp_years = fields.Integer(string="Kinh nghiệm (năm)")

    headline = fields.Char(string="Tiêu đề hồ sơ")
    location = fields.Char(string="Địa điểm")

    avatar = fields.Binary(string="Ảnh đại diện")

    skill_ids = fields.Many2many('dumuc.skill', string="Kỹ năng")

    experience_ids = fields.One2many('dumuc.seeker.experience', 'seeker_id', string="Kinh nghiệm")

    created_at = fields.Datetime(string="Ngày tạo", default=fields.Datetime.now)

    application_ids = fields.One2many('dumuc.job.application', 'seeker_id', string="Ứng tuyển")

    is_public = fields.Boolean(default=True, string="Công khai")

    phone_unlocked_by = fields.Many2many('dumuc.company', string="Garage đã mở khóa")

    
    def unlock_phone(self, company):
        if not self.is_public:
            raise UserError("Hồ sơ không công khai.")

        if company in self.phone_unlocked_by:
            return

        if company.credit_balance < 5:
            raise UserError("Không đủ credit để xem số điện thoại.")

        company.spend_credit(5, "Xem hồ sơ ứng viên")
        self.phone_unlocked_by = [(4, company.id)]


class SeekerUnlock(models.Model):
    _name = "dumuc.seeker.unlock"

    company_id = fields.Many2one("dumuc.company")
    seeker_id = fields.Many2one("dumuc.job.seeker")
    unlocked_at = fields.Datetime(default=fields.Datetime.now)