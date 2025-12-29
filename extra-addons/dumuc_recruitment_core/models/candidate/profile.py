from odoo import models, fields


class CandidateProfile(models.Model):
    _name = "dumuc.candidate.profile"
    _description = "Hồ sơ ứng viên"

    user_id = fields.Many2one(
        "res.users",
        string="Tài khoản người dùng",
        required=True
    )

    bio = fields.Text(
        string="Giới thiệu bản thân"
    )

    location = fields.Char(
        string="Khu vực"
    )

    rate_day = fields.Float(
        string="Mức lương theo ngày"
    )

    availability = fields.Selection([
        ('immediate', 'Có thể đi làm ngay'),
        ('scheduled', 'Đi làm theo lịch'),
        ('unavailable', 'Chưa có nhu cầu')
    ], string="Trạng thái sẵn sàng", default="immediate")

    skill_ids = fields.Many2many(
        "dumuc.skill.detail",
        string="Kỹ năng"
    )

    experience_ids = fields.One2many(
        "dumuc.candidate.experience",
        "candidate_id",
        string="Kinh nghiệm làm việc"
    )

    education_ids = fields.One2many(
        "dumuc.candidate.education",
        "candidate_id",
        string="Học vấn"
    )

    certification_ids = fields.One2many(
        "dumuc.candidate.certification",
        "candidate_id",
        string="Chứng chỉ"
    )

    portfolio_ids = fields.One2many(
        "dumuc.candidate.portfolio",
        "candidate_id",
        string="Dự án"
    )

    saved_job_ids = fields.One2many(
        "dumuc.candidate.saved.job",
        "candidate_id",
        string="Tin đã lưu"
    )

    kyc_id = fields.Many2one(
        "dumuc.candidate.kyc",
        string="Xác thực danh tính"
    )

    applicant_ids = fields.One2many(
        "hr.applicant",
        "candidate_id",
        string="Lịch sử ứng tuyển"
    )

    matching_score = fields.Float(
        string="Điểm matching",
        help="Điểm phù hợp tổng quan"
    )

    def action_apply(self, job):
        """Ứng tuyển một tin tuyển dụng"""
        return self.env["hr.applicant"].create({
            "candidate_id": self.id,
            "job_id": job.id
        })

    def action_save_job(self, job):
        """Lưu tin"""
        return self.env["dumuc.candidate.saved.job"].create({
            "candidate_id": self.id,
            "job_id": job.id
        })
