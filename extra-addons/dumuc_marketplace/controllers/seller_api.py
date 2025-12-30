# -*- coding: utf-8 -*-

from odoo import http
from market_base import MarketControllerBase
from dumuc_identity_core.controllers.helpers import api_ok, api_error, get_json


class SellerListingAPI(MarketControllerBase):

    # ----------------------------------------------------
    # 1) Lấy danh sách tin đăng của Seller
    # ----------------------------------------------------
    @http.route("/api/market/seller/listings/my", type="json", auth="public", csrf=False)
    def my_listings(self, **kw):

        ctx, err = self._auth()
        if err:
            return err

        user = ctx["user"]

        listings = http.request.env["dumuc.listing"].sudo().search([
            ("partner_id", "=", user.partner_id.id)
        ])

        return api_ok([
            {
                "id": l.id,
                "title": l.name,
                "price": l.price,
                "state": l.state,
                "is_free_quota": l.is_free_quota,
                "posted_at": str(l.posted_at) if l.posted_at else None,
            }
            for l in listings
        ])


    # ----------------------------------------------------
    # 2) Tạo tin đăng mới (Draft)
    # ----------------------------------------------------
    @http.route("/api/market/seller/listing/create", type="json", auth="public", csrf=False)
    def create_listing(self, **kw):

        ctx, err = self._auth()
        if err:
            return err

        user = ctx["user"]
        data = get_json()

        Listing = http.request.env["dumuc.listing"].sudo()

        rec = Listing.create({
            "name": data.get("title"),
            "price": data.get("price"),
            "description": data.get("description"),
            "partner_id": user.partner_id.id,
            "state": "draft",
        })

        return api_ok({"id": rec.id})


    # ----------------------------------------------------
    # 3) Cập nhật tin (chỉ khi draft / rejected)
    # ----------------------------------------------------
    @http.route("/api/market/seller/listing/update", type="json", auth="public", csrf=False)
    def update_listing(self, **kw):

        ctx, err = self._auth()
        if err:
            return err

        user = ctx["user"]
        data = get_json()

        listing_id = data.get("listing_id")

        rec = http.request.env["dumuc.listing"].sudo().browse(listing_id)

        if not rec or rec.partner_id.id != user.partner_id.id:
            return api_error("ACCESS_DENIED", "Bạn không có quyền sửa tin này")

        if rec.state not in ("draft", "rejected"):
            return api_error("INVALID_STATE", "Chỉ sửa tin khi đang ở trạng thái Nháp hoặc Bị Từ Chối")

        rec.write({
            "name": data.get("title", rec.name),
            "price": data.get("price", rec.price),
            "description": data.get("description", rec.description),
        })

        return api_ok({"updated": True})


    # ----------------------------------------------------
    # 4) Gửi tin đi duyệt
    # ----------------------------------------------------
    @http.route("/api/market/seller/listing/submit_review", type="json", auth="public", csrf=False)
    def submit_review(self, **kw):

        ctx, err = self._auth()
        if err:
            return err

        user = ctx["user"]
        data = get_json()

        rec = http.request.env["dumuc.listing"].sudo().browse(data.get("listing_id"))

        if not rec or rec.partner_id.id != user.partner_id.id:
            return api_error("ACCESS_DENIED", "Không được gửi duyệt tin của người khác")

        try:
            rec.action_submit_for_review()
        except Exception as e:
            return api_error("SUBMIT_FAILED", str(e))

        return api_ok({"status": rec.state})


    # ----------------------------------------------------
    # 5) Đánh dấu đã bán
    # ----------------------------------------------------
    @http.route("/api/market/seller/listing/mark_sold", type="json", auth="public", csrf=False)
    def mark_sold(self, **kw):

        ctx, err = self._auth()
        if err:
            return err

        user = ctx["user"]
        data = get_json()

        rec = http.request.env["dumuc.listing"].sudo().browse(data.get("listing_id"))

        if not rec or rec.partner_id.id != user.partner_id.id:
            return api_error("ACCESS_DENIED", "Không được thao tác tin của người khác")

        rec.action_mark_as_sold()

        return api_ok({"status": rec.state})

    # ----------------------------------------------------
    # 6) Kiểm tra trạng thái QUOTA (Số lần đăng tin miễn phí hay combo)
    # ----------------------------------------------------
    @http.route("/api/market/seller/quota/status", type="json", auth="public", csrf=False)
    def quota_status(self, **kw):

        ctx, err = self._auth()
        if err:
            return err

        user = ctx["user"]
        partner = user.partner_id.sudo()

        max_free = int(
            http.request.env["ir.config_parameter"]
            .sudo()
            .get_param("dumuc.max_free_posts", 5)
        )

        used = partner.dumuc_free_post_used or 0

        return api_ok({
            "max_free_posts": max_free,
            "used_free_posts": used,
            "remaining_free_posts": max_free - used if used < max_free else 0,
            "has_free_post_available": used < max_free
        })

    # ----------------------------------------------------
    # 7) Check quyền đăng tin trước khi submit
    # ----------------------------------------------------
    @http.route("/api/market/seller/quota/can_submit", type="json", auth="public", csrf=False)
    def quota_check_submit(self, **kw):

        ctx, err = self._auth()
        if err:
            return err

        user = ctx["user"]
        partner = user.partner_id.sudo()

        max_free = int(
            http.request.env["ir.config_parameter"]
            .sudo()
            .get_param("dumuc.max_free_posts", 5)
        )

        used = partner.dumuc_free_post_used or 0

        if used >= max_free:
            return api_error(
                "QUOTA_EXCEEDED",
                "Bạn đã hết lượt đăng miễn phí. Vui lòng mua gói dịch vụ."
            )

        return api_ok({
            "can_submit": True,
            "remaining_free_posts": max_free - used
       
        })

    
    # ----------------------------------------------------
    # 8) Dùng package để đăng tin
    # ----------------------------------------------------
    @http.route("/api/market/seller/package/use", type="json", auth="public", csrf=False)
    def use_package_for_listing(self, **kw):

        ctx, err = self._auth()
        if err:
            return err

        user = ctx["user"]
        data = http.request.jsonrequest

        listing = http.request.env["dumuc.listing"].sudo().browse(data.get("listing_id"))

        if not listing or listing.partner_id.id != user.partner_id.id:
            return api_error("ACCESS_DENIED", "Không thể sử dụng gói cho tin của người khác")

        Usage = http.request.env["dumuc.package.usage"].sudo()

        try:
            usage = Usage.use_post_package(user.partner_id, listing)
        except Exception as e:
            return api_error("PACKAGE_FAILED", str(e))

        return api_ok({
            "package_id": usage.package_id.id,
            "usage_id": usage.id,
            "listing_state": listing.state,
            "used_from_package": True
        })


    