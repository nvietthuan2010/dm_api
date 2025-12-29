from odoo import models, fields


class MatchingConfig(models.Model):
    _name = "dumuc.match.config"
    _description = "Cấu hình thuật toán matching Gig"

    weight_skill = fields.Float(
        string="Trọng số kỹ năng",
        default=0.45,
        help="Tỷ lệ đánh giá kỹ năng"
    )

    weight_distance = fields.Float(
        string="Trọng số khoảng cách",
        default=0.25,
        help="Tỷ lệ đánh giá khoảng cách"
    )

    weight_rate = fields.Float(
        string="Trọng số mức giá",
        default=0.15,
        help="Tỷ lệ đánh giá mức giá"
    )

    weight_availability = fields.Float(
        string="Trọng số trạng thái sẵn sàng",
        default=0.15,
        help="Tỷ lệ đánh giá tình trạng online/offline"
    )

    urgent_bonus = fields.Float(
        string="Điểm thưởng khẩn cấp",
        default=10.0,
        help="Điểm cộng cho gig đánh dấu khẩn cấp"
    )
