from odoo import models, fields


class DumucInspectionTemplate(models.Model):
    _name = "dumuc.inspection.template"
    _description = "Template kiểm định"
    _order = "sequence,id"

    name = fields.Char("Tên bộ kiểm định", required=True)
    sequence = fields.Integer(default=10)
    version = fields.Char("Phiên bản", default="1.0")
    description = fields.Text("Mô tả")
    is_active = fields.Boolean("Kích hoạt", default=True)

    group_ids = fields.One2many(
        "dumuc.inspection.group",
        "template_id",
        string="Nhóm kiểm tra"
    )

class DumucInspectionGroup(models.Model):
    _name = "dumuc.inspection.group"
    _description = "Nhóm kiểm định"
    _order = "sequence,id"

    name = fields.Char("Tên nhóm mục", required=True)
    sequence = fields.Integer(default=10)

    template_id = fields.Many2one(
        "dumuc.inspection.template",
        string="Bộ kiểm định",
        required=True
    )

    criteria_ids = fields.One2many(
        "dumuc.inspection.criteria",
        "group_id",
        string="Các mục kiểm tra"
    )

class DumucInspectionCriteria(models.Model):
    _name = "dumuc.inspection.criteria"
    _description = "Hạng mục kiểm định"
    _order = "sequence,id"

    name = fields.Char("Tên hạng mục", required=True)
    sequence = fields.Integer(default=10)

    group_id = fields.Many2one(
        "dumuc.inspection.group",
        string="Nhóm kiểm tra",
        required=True
    )

    required_photo = fields.Boolean("Phải chụp ảnh?")
    
    description = fields.Text("Mô tả")
