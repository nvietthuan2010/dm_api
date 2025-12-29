from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class Job(models.Model):
    _name = 'dumuc.job'
    _description = "Tin tuyển dụng"

    name = fields.Char(string="Tiêu đề", required=True)
    description = fields.Html(string="Mô tả")

    salary_min = fields.Float(string="Lương tối thiểu")
    salary_max = fields.Float(string="Lương tối đa")
    
    salary_unit = fields.Selection([
        ('month', "Tháng"),
        ('day', "Ngày"),
        ('hour', "Giờ"),
        ('job', "Việc"),
    ], string="Đơn vị lương")

    employment_type = fields.Selection([
        ('full_time', "Toàn thời gian"),
        ('part_time', "Bán thời gian"),
        ('seasonal', "Theo mùa"),
        ('project', "Dự án"),
    ], string="Hình thức làm việc")

    category_id = fields.Many2one('dumuc.job.category', string="Ngành nghề")
    company_id = fields.Many2one('dumuc.company', string="Công ty")
    employer_id = fields.Many2one('res.users', string="Người đăng")

    location = fields.Char(string="Địa điểm làm việc")

    status = fields.Selection([
        ('draft', "Nháp"),
        ('pending', "Chờ duyệt"),
        ('approved', "Đã duyệt"),
        ('active', "Đang tuyển"),
        ('expired', "Hết hạn"),
        ('rejected', "Từ chối"),
    ], default='draft', string="Trạng thái")

    is_urgent = fields.Boolean(string="Khẩn cấp", default=False)
    quantity = fields.Integer(string="Số lượng")

    start_date = fields.Date(string="Ngày bắt đầu")
    end_date = fields.Date(string="Ngày kết thúc")
    expires_at = fields.Datetime(string="Hết hạn")

    created_at = fields.Datetime(string="Ngày tạo", default=fields.Datetime.now)

    application_ids = fields.One2many('dumuc.job.application', 'job_id', string="Ứng tuyển")


    @api.constrains('salary_min', 'salary_max')
    def _check_salary_range(self):
        for job in self:
            if job.salary_min and job.salary_max and job.salary_min > job.salary_max:
                raise ValidationError("Lương tối thiểu phải nhỏ hơn hoặc bằng mức tối đa.")

    def action_submit(self):
        for job in self:
            if job.status != 'draft':
                raise UserError("Chỉ được gửi duyệt khi trạng thái đang là Nháp.")
            job.status = 'pending'

    def action_resubmit(self):
        for job in self:
            if job.status != 'rejected':
                raise UserError("Chỉ được gửi duyệt lại khi trạng thái từ chối.")
            job.status = 'pending'

    def action_approve(self):
        for job in self:
            if job.status != 'pending':
                raise UserError("Chỉ duyệt tin đang Chờ duyệt.")
            
            company = job.company_id
            
            if company.verify_status != 'verified':
                raise UserError("Garage chưa xác thực. Không thể duyệt tin.")

            cost = 10
            if company.credit_balance < cost:
                raise UserError("Không đủ credit để duyệt tin.")

            company.spend_credit(cost, "Đăng tin tuyển dụng")
            job.status = 'active'

    def action_reject(self):
        for job in self:
            if job.status != 'pending':
                raise UserError("Chỉ từ chối tin đang Chờ duyệt.")
            job.status = 'rejected'

    def action_close(self):
        for job in self:
            if job.status != 'active':
                raise UserError("Chỉ đóng tin đang hiển thị.")
            job.status = 'closed'

    @api.model
    def cron_expire_jobs(self):
        now = fields.Datetime.now()
        jobs = self.search([
            ('status', '=', 'active'),
            ('expires_at', '<', now)
        ])
        for job in jobs:
            job.status = 'expired'