from odoo import models, fields


class ScreeningQuestion(models.Model):
    _name = "dumuc.screening.question"
    _description = "Câu hỏi sàng lọc ứng viên"

    job_id = fields.Many2one("hr.job", string="Tin tuyển dụng")

    question = fields.Char(
        string="Nội dung câu hỏi",
        required=True
    )

    required = fields.Boolean(
        string="Bắt buộc trả lời",
        default=False
    )

    reject_if_fail = fields.Boolean(
        string="Loại ứng viên nếu trả lời sai",
        default=False
    )
