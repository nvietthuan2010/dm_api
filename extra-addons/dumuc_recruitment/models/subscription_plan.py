class SubscriptionPlan(models.Model):
    _name = "dumuc.subscription.plan"
    _description = "Gói Subscription"

    name = fields.Char(required=True)
    monthly_credits = fields.Integer("Số credit mỗi tháng", required=True)
    price_vnd = fields.Integer("Giá / tháng", required=True)
    is_active = fields.Boolean(default=True)

    description = fields.Text()
