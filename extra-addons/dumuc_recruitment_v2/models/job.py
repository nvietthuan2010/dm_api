from odoo import models, fields, api
from odoo.exceptions import ValidationError
import json

class DumucJob(models.Model):
    _name = "dumuc.job"
    _description = "Recruitment Job"
    _order = "created_at desc"
    _rec_name = "title"

    # ==================================================
    # RELATION
    # ==================================================

    company_id = fields.Many2one(
        "dumuc.company",
        string="Công ty",
        required=True,
        ondelete="cascade",
        index=True
    )

    # ==================================================
    # BASIC INFO
    # ==================================================

    title = fields.Char(
        string="Tiêu đề",
        required=True
    )

    description = fields.Html(
        string="Mô tả công việc",
        sanitize=True
    )

    location = fields.Char(
        string="Địa điểm làm việc"
    )

    quantity = fields.Integer(
        string="Số lượng tuyển",
        default=1
    )

    # ==================================================
    # SALARY
    # ==================================================

    salary_min = fields.Integer(string="Lương tối thiểu")
    salary_max = fields.Integer(string="Lương tối đa")

    salary_unit = fields.Selection(
        [
            ("month", "Theo tháng"),
            ("day", "Theo ngày"),
            ("hour", "Theo giờ"),
            ("job", "Theo công việc"),
        ],
        default="month"
    )

    # ==================================================
    # TYPE
    # ==================================================

    employment_type = fields.Selection(
        [
            ("full_time", "Toàn thời gian"),
            ("part_time", "Bán thời gian"),
            ("seasonal", "Thời vụ"),
            ("project", "Theo dự án"),
        ],
        default="full_time"
    )

    # ==================================================
    # STATUS
    # ==================================================

    # ==================================================
    # TIME
    # ==================================================

    published_at = fields.Datetime(
        string="Ngày đăng",
        readonly=True
    )

    expires_at = fields.Datetime(
        string="Ngày hết hạn"
    )

    created_at = fields.Datetime(
        string="Ngày tạo",
        default=fields.Datetime.now,
        readonly=True
    )

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('approved', 'Đã duyệt'),
        ('pending_review', 'Chờ duyệt lại'),
        ('rejected', 'Từ chối'),
        ('archived', 'Đã lưu trữ'),
    ], default='draft', string="Trạng thái tin tuyển dụng")

    # ===== REVISION CONTROL =====
    review_state = fields.Selection([
        ('none', 'Không có'),
        ('pending_review', 'Đang chờ duyệt lại'),
        ('approved_after_review', 'Đã duyệt sau chỉnh sửa'),
        ('rejected_after_review', 'Bị từ chối sau chỉnh sửa'),
    ], default='none', string="Trạng thái kiểm duyệt lại")

    revision_seq = fields.Integer(
        string="Số lần chỉnh sửa",
        default=0
    )

    pending_review_at = fields.Datetime("Thời điểm gửi duyệt lại")
    pending_review_by = fields.Many2one("res.users", string="Người gửi duyệt")

    review_decision_at = fields.Datetime("Thời điểm ra quyết định")
    review_decision_by = fields.Many2one("res.users", string="Người duyệt")
    review_reject_reason = fields.Text("Lý do từ chối chỉnh sửa")

    # ===== SNAPSHOTS =====
    approved_payload_json = fields.Text("Payload đang public")
    pending_payload_json = fields.Text("Payload chỉnh sửa (chờ duyệt)")

    # ===== APPLY CONTROL =====
    is_locked_for_review = fields.Boolean(
        string="Khoá nhận hồ sơ khi chờ duyệt",
        default=False
    )

    # ==================================================
    # BUSINESS METHODS (MVP)
    # ==================================================

    # ==================================================
    # CONSTRAINTS
    # ==================================================

    @api.constrains("salary_min", "salary_max")
    def _check_salary_range(self):
        for job in self:
            if (
                job.salary_min
                and job.salary_max
                and job.salary_min > job.salary_max
            ):
                raise ValidationError(
                    "Lương tối thiểu không được lớn hơn lương tối đa"
                )

    def _build_current_payload(self):
        return {
            "title": self.title,
            "description": self.description,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "employment_type": self.employment_type,
            "location": self.location,
        }
    
    def action_mark_approved(self):
        for job in self:
            job.status = "approved"
            job.review_state = "none"
            job.revision_seq = 0
            job.is_locked_for_review = False

            job.approved_payload_json = json.dumps(
                job._build_current_payload(),
                ensure_ascii=False
            )

    @api.model
    def _fields_trigger_review(self):
        return [
            "title",
            "description",
            "salary_min",
            "salary_max",
            "employment_type",
            "location",
        ]

    def write(self, vals):
        for job in self:

            # Không áp dụng nếu chưa từng được duyệt
            if job.status != "approved":
                return super(DumucJob, job).write(vals)

            trigger_fields = self._fields_trigger_review()
            changed = any(f in vals for f in trigger_fields)

            if not changed:
                # thay đổi không quan trọng → update bình thường
                return super(DumucJob, job).write(vals)

            # ====== STORE EDITED PAYLOAD TO PENDING ======
            updated_values = job._build_current_payload()
            for f in trigger_fields:
                if f in vals:
                    updated_values[f] = vals[f]

            job.pending_payload_json = json.dumps(
                updated_values,
                ensure_ascii=False
            )

            # ====== FLAG FOR REVIEW ======
            job.review_state = "pending_review"
            job.status = "approved"          # vẫn public
            job.is_locked_for_review = True  # khoá apply tạm thời
            job.revision_seq += 1
            job.pending_review_at = fields.Datetime.now()
            job.pending_review_by = self.env.user

        return super(DumucJob, self).write(vals)
