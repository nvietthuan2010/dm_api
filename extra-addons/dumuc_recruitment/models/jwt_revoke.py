class JWTBlacklist(models.Model):
    _name = "jwt.blacklist"
    _description = "JWT Revocation List"

    jti = fields.Char(required=True, index=True)
    revoked_at = fields.Datetime(default=fields.Datetime.now)
