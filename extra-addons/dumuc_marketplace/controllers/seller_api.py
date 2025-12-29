# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError, AccessError


# ---------------------------
# Response helper
# ---------------------------

def api_ok(data=None):
    return {"success": True, "data": data, "error": None}


def api_error(code, message):
    return {
        "success": False,
        "data": None,
        "error": {"code": code, "message": message}
    }


# ---------------------------
# Helpers
# ---------------------------

def _require_seller():
    user = request.env.user

    if user.role_type not in ("private", "salon"):
        raise AccessError("Người dùng không phải Seller")

    return user


def _ensure_owner(record, user):
    if not record or record.partner_id.id != user.partner_id.id:
        raise AccessError("Không có quyền thao tác trên bản ghi này")


# ---------------------------
# SELLER API CONTROLLER
# ---------------------------

class SellerAPI(http.Controller):

    # ---------------------------
    #  LISTING — CREATE DRAFT
    # ---------------------------

    @http.route('/api/market/seller/listing/create',
                type='json', auth='user', methods=['POST'])
    def create_listing(self, **payload):
        try:
            user = _require_seller()

            vals = {
                "name": payload.get("title"),
                "partner_id": user.partner_id.id,
                "price": payload.get("price"),
                "brand_id": payload.get("brand_id"),
                "model_id": payload.get("model_id"),
                "year": payload.get("year"),
                "mileage": payload.get("mileage"),
                "description": payload.get("description"),
                "state": "draft",
            }

            rec = request.env["dumuc.listing"].sudo().create(vals)

            return api_ok({
                "listing_id": rec.id,
                "state": rec.state,
            })

        except Exception as e:
            return api_error("CREATE_FAILED", str(e))

    # ---------------------------
    # UPDATE LISTING
    # ---------------------------

    @http.route('/api/market/seller/listing/update',
                type='json', auth='user', methods=['POST'])
    def update_listing(self, listing_id=None, **payload):
        try:
            user = _require_seller()

            listing = request.env["dumuc.listing"].sudo().browse(listing_id)
            _ensure_owner(listing, user)

            if listing.state not in ("draft", "rejected"):
                raise UserError("Chỉ sửa tin Nháp hoặc Bị từ chối")

            allowed = ["name", "price", "description", "year", "mileage"]

            listing.write({k: v for k, v in payload.items() if k in allowed})

            return api_ok({"listing_id": listing.id})

        except (UserError, AccessError) as e:
            return api_error("UPDATE_DENIED", str(e))

        except Exception as e:
            return api_error("UPDATE_FAILED", str(e))

    # ---------------------------
    # SUBMIT FOR REVIEW
    # ---------------------------

    @http.route('/api/market/seller/listing/submit',
                type='json', auth='user', methods=['POST'])
    def submit_listing(self, listing_id):
        try:
            user = _require_seller()

            listing = request.env["dumuc.listing"].sudo().browse(listing_id)
            _ensure_owner(listing, user)

            listing.action_submit_for_review()

            return api_ok({"state": listing.state})

        except UserError as e:
            return api_error("SUBMIT_REJECTED", str(e))

        except Exception as e:
            return api_error("SUBMIT_FAILED", str(e))

    # ---------------------------
    # MARK AS SOLD
    # ---------------------------

    @http.route('/api/market/seller/listing/mark_sold',
                type='json', auth='user', methods=['POST'])
    def mark_sold(self, listing_id):
        try:
            user = _require_seller()

            listing = request.env["dumuc.listing"].sudo().browse(listing_id)
            _ensure_owner(listing, user)

            listing.action_mark_as_sold()

            return api_ok({"state": listing.state})

        except Exception as e:
            return api_error("MARK_SOLD_FAILED", str(e))

    # ---------------------------
    # MY LISTINGS
    # ---------------------------

    @http.route('/api/market/seller/listing/mine',
                type='json', auth='user', methods=['GET'])
    def my_listings(self):
        try:
            user = _require_seller()

            recs = request.env["dumuc.listing"].sudo().search([
                ("partner_id", "=", user.partner_id.id)
            ])

            return api_ok([
                {
                    "id": r.id,
                    "title": r.name,
                    "state": r.state,
                    "price": r.price,
                    "is_featured": r.is_featured,
                    "priority_score": r.priority_score,
                }
                for r in recs
            ])

        except Exception as e:
            return api_error("FETCH_FAILED", str(e))

    # ---------------------------
    # PUSH LISTING
    # ---------------------------

    @http.route('/api/market/seller/listing/push',
                type='json', auth='user', methods=['POST'])
    def push(self, listing_id):
        try:
            user = _require_seller()

            listing = request.env["dumuc.listing"].sudo().browse(listing_id)
            _ensure_owner(listing, user)

            listing.action_push()

            return api_ok({"status": "pushed"})

        except UserError as e:
            return api_error("PUSH_REJECTED", str(e))

        except Exception as e:
            return api_error("PUSH_FAILED", str(e))

    # ---------------------------
    # RENEW LISTING
    # ---------------------------

    @http.route('/api/market/seller/listing/renew',
                type='json', auth='user', methods=['POST'])
    def renew(self, listing_id):
        try:
            user = _require_seller()

            listing = request.env["dumuc.listing"].sudo().browse(listing_id)
            _ensure_owner(listing, user)

            listing.action_renew()

            return api_ok({"status": "renewed"})

        except UserError as e:
            return api_error("RENEW_REJECTED", str(e))

        except Exception as e:
            return api_error("RENEW_FAILED", str(e))

    # ---------------------------
    # WALLET INFO
    # ---------------------------

    @http.route('/api/market/seller/wallet/info',
                type='json', auth='user', methods=['GET'])
    def wallet_info(self):
        try:
            user = _require_seller()

            return api_ok({
                "balance": user.wallet_balance,
            })

        except Exception as e:
            return api_error("WALLET_FAILED", str(e))

    # ---------------------------
    # WALLET TRANSACTIONS
    # ---------------------------

    @http.route('/api/market/seller/wallet/transactions',
                type='json', auth='user', methods=['GET'])
    def wallet_transactions(self):
        try:
            user = _require_seller()

            txs = request.env["dumuc.transaction"].sudo().search([
                ("user_id", "=", user.id)
            ], order="id desc")

            return api_ok([
                {
                    "id": t.id,
                    "type": t.type,
                    "amount": t.amount,
                    "status": t.status,
                }
                for t in txs
            ])

        except Exception as e:
            return api_error("TX_FETCH_FAILED", str(e))
