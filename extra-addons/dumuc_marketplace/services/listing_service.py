from odoo import _, fields
from odoo.exceptions import UserError

MAX_FREE_DEFAULT = 5  # TODO: đọc từ ir.config_parameter


class ListingService:
    """Service xử lý nghiệp vụ Listing cho Domain Marketplace."""

    def __init__(self, env):
        self.env = env

    def search_listings(self, filters, sort="recent", limit=20, offset=0):
        """
        filters: dict như {
          'brand_id': 1,
          'model_id': 2,
          'price_min': 300,
          'price_max': 800,
          'year_min': 2015,
          'year_max': 2020,
          'province_id': 79,
          'body_style': 'suv',
          'is_certified': True,
        }
        """
        # build domain
        domain = [("state", "=", "active"), ("is_blocked", "=", False)]
        # ... build thêm domain theo filters ...

        Listing = self.env["dumuc.listing"].sudo()
        records = Listing.search(domain, limit=limit, offset=offset, order=self._map_sort(sort))
        return records

    def _map_sort(self, sort):
        if sort == "price_asc":
            return "price asc"
        if sort == "price_desc":
            return "price desc"
        if sort == "year_desc":
            return "year desc"
        if sort == "view_desc":
            return "view_count desc"
        # default: mới nhất
        return "posted_at desc"
    
    # -------- Helper --------
    def _get_max_free_posts(self):
        # tạm: hard-code; sau này dùng ir.config_parameter
        param = self.env["ir.config_parameter"].sudo().get_param(
            "dumuc.max_free_posts"
        )
        if param:
            try:
                return int(param)
            except Exception:
                pass
        return MAX_FREE_DEFAULT

    def _has_free_quota(self, partner):
        return partner.dumuc_free_post_used < self._get_max_free_posts()

    def _create_history(self, listing, action, admin=None, note=None):
        self.env["dumuc.listing.history"].sudo().create({
            "listing_id": listing.id,
            "action": action,
            "admin_id": admin.id if admin else False,
            "note": note or "",
            "action_time": fields.Datetime.now(),
        })

    # -------- Public APIs --------
    def create_draft(self, user, vals):
        """Tạo tin nháp (Portal Seller sẽ dùng)."""
        vals = dict(vals)
        vals.setdefault("user_id", user.id)
        vals.setdefault("state", "draft")
        listing = self.env["dumuc.listing"].sudo().create(vals)
        self._create_history(listing, "edit", admin=None, note="Tạo nháp")
        return listing

    def submit_listing(self, listing):
        """Seller gửi tin đi duyệt.

        Logic:
        - nếu partner còn quota free: dùng free, state = 'pending'
        - nếu hết: state = 'awaiting_payment'
        """
        partner = listing.partner_id
        if listing.state not in ("draft", "rejected"):
            raise UserError(_("Chỉ tin nháp hoặc bị từ chối mới được gửi duyệt."))

        if self._has_free_quota(partner):
            listing.write({
                "is_free_quota": True,
                "state": "pending",
            })
            partner.sudo().dumuc_free_post_used += 1
            self._create_history(listing, "submit", note="Gửi duyệt (dùng suất miễn phí)")
        else:
            listing.write({
                "is_free_quota": False,
                "state": "awaiting_payment",
            })
            self._create_history(listing, "submit", note="Gửi duyệt (chờ thanh toán)")
        return listing

    def mark_paid_and_send_to_pending(self, listing):
        """Được gọi bởi domain Finance sau khi thanh toán phí đăng tin."""
        if listing.state != "awaiting_payment":
            raise UserError(_("Tin không ở trạng thái chờ thanh toán."))
        listing.write({"state": "pending"})
        self._create_history(listing, "submit", note="Thanh toán xong, chuyển chờ duyệt")
        return listing

    def admin_approve(self, listing, admin):
        """Admin duyệt tin."""
        if listing.state not in ("pending", "awaiting_payment"):
            raise UserError(_("Chỉ duyệt tin ở trạng thái chờ duyệt hoặc chờ thanh toán."))

        listing.write({
            "state": "active",
            "posted_at": fields.Datetime.now(),
            "moderation_admin_id": admin.id,
            "moderation_time": fields.Datetime.now(),
            "reject_reason_id": False,
            "moderation_note": False,
        })
        self._create_history(listing, "approve", admin=admin, note="Duyệt tin")
        return listing

    def admin_reject(self, listing, admin, reason_id=False, note=False):
        """Admin từ chối tin."""
        if listing.state not in ("pending", "awaiting_payment"):
            raise UserError(_("Chỉ từ chối tin ở trạng thái chờ duyệt/chờ thanh toán."))

        vals = {
            "state": "rejected",
            "moderation_admin_id": admin.id,
            "moderation_time": fields.Datetime.now(),
        }
        if reason_id:
            vals["reject_reason_id"] = reason_id
        if note:
            vals["moderation_note"] = note

        listing.write(vals)
        self._create_history(listing, "reject", admin=admin, note=note)
        return listing

    def block_listing(self, listing, admin, note=False):
        """Admin chặn tin vĩnh viễn."""
        listing.write({
            "state": "blocked",
            "is_blocked": True,
        })
        self._create_history(listing, "block", admin=admin, note=note or "Blocked by admin")
        return listing
    
    def increase_view(self, listing):
        listing.sudo().write({
            "view_count": listing.view_count + 1
        })
    
    def _charge_for_posting(self, partner, amount, description='Phí đăng tin'):
        Transaction = self.env['dumuc.transaction']
        Wallet = self.env['res.partner'].sudo().browse(partner.id)
        if Wallet.dumuc_wallet_balance < amount:
            raise UserError(_("Số dư không đủ, vui lòng nạp ví."))
        Wallet.sudo().write({'dumuc_wallet_balance': Wallet.dumuc_wallet_balance - amount})
        Transaction.sudo().create({
            'partner_id': partner.id,
            'amount': amount,
            'direction': 'out',
            'transaction_type': 'posting_fee',
            'state': 'done',
            'description': description,
        })
        return True


