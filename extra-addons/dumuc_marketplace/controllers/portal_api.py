# controllers/portal_api.py
from odoo import http
from odoo.http import request, Response
import json
from datetime import datetime

class DumucPortalAPI(http.Controller):

    # public listings (homepage)
    @http.route(['/dumuc/api/listings'], type='json', auth='public', methods=['POST'], csrf=False)
    def api_listings(self, **post):
        # post expects filters dict: {brand_id, model_id, price_min, price_max, page, per_page, sort}
        filters = post.get('filters') or {}
        page = int(post.get('page', 1))
        per_page = int(post.get('per_page', 20))
        domain = [('state', '=', 'active'), ('is_blocked', '=', False)]
        if filters.get('brand_id'):
            domain.append(('brand_id', '=', int(filters['brand_id'])))
        if filters.get('model_id'):
            domain.append(('model_id', '=', int(filters['model_id'])))
        if filters.get('price_min'):
            domain.append(('price', '>=', float(filters['price_min'])))
        if filters.get('price_max'):
            domain.append(('price', '<=', float(filters['price_max'])))
        Listing = request.env['dumuc.listing'].sudo()
        order = 'priority_score desc, posted_at desc'
        offset = (page - 1) * per_page
        recs = Listing.search(domain, limit=per_page, offset=offset, order=order)
        results = []
        for r in recs:
            results.append({
                'id': r.id,
                'title': r.name,
                'price': r.price,
                'brand': r.brand_id.name if r.brand_id else False,
                'model': r.model_id.name if r.model_id else False,
                'cover_image': r.cover_image.decode('utf-8') if r.cover_image else False,
                'slug': r.slug if hasattr(r, 'slug') else False,
                'is_certified': bool(r.inspection_result_id),
            })
        return {'page': page, 'per_page': per_page, 'items': results}

    # public listing detail
    @http.route(['/dumuc/api/listing/<int:listing_id>'], type='json', auth='public', methods=['GET'], csrf=False)
    def api_listing_detail(self, listing_id, **kw):
        Listing = request.env['dumuc.listing'].sudo().browse(int(listing_id))
        if not Listing.exists() or Listing.state != 'active':
            return Response(json.dumps({'error': 'not_found'}), status=404, mimetype='application/json')
        # increase view count
        try:
            Listing.sudo().write({'view_count': (Listing.view_count or 0) + 1})
        except Exception:
            pass
        data = {
            'id': Listing.id,
            'title': Listing.name,
            'price': Listing.price,
            'brand': Listing.brand_id.name if Listing.brand_id else False,
            'model': Listing.model_id.name if Listing.model_id else False,
            'description': Listing.description,
            'images': [{'id': i.id, 'caption': i.caption} for i in Listing.image_ids],
            'inspection_report': Listing.inspection_result_id.id if Listing.inspection_result_id else False,
        }
        return data

    # private: create listing (seller must be logged in)
    @http.route(['/dumuc/api/seller/listing/create'], type='json', auth='user', methods=['POST'], csrf=False)
    def api_seller_create_listing(self, **post):
        # require fields: name, price, brand_id, model_id, description
        data = post.get('data') or {}
        partner = request.env.user.partner_id.sudo()
        vals = {
            'name': data.get('name'),
            'price': float(data.get('price') or 0.0),
            'partner_id': partner.id,
            'brand_id': int(data.get('brand_id')) if data.get('brand_id') else False,
            'model_id': int(data.get('model_id')) if data.get('model_id') else False,
            'description': data.get('description') or '',
        }
        rec = request.env['dumuc.listing'].sudo().create(vals)
        return {'id': rec.id, 'message': 'created'}

    # private: submit listing for review
    @http.route(['/dumuc/api/seller/listing/<int:listing_id>/submit'], type='json', auth='user', methods=['POST'], csrf=False)
    def api_seller_submit_listing(self, listing_id, **post):
        rec = request.env['dumuc.listing'].sudo().browse(int(listing_id))
        if not rec.exists() or rec.partner_id.id != request.env.user.partner_id.id:
            return Response(json.dumps({'error': 'forbidden'}), status=403, mimetype='application/json')
        try:
            rec.sudo().action_submit_for_review()
        except Exception as e:
            return {'error': str(e)}
        return {'status': 'ok'}

    # private: upload image (base64)
    @http.route(['/dumuc/api/seller/listing/<int:listing_id>/image'], type='json', auth='user', methods=['POST'], csrf=False)
    def api_seller_upload_image(self, listing_id, **post):
        rec = request.env['dumuc.listing'].sudo().browse(int(listing_id))
        partner = request.env.user.partner_id
        if not rec.exists() or rec.partner_id.id != partner.id:
            return Response(json.dumps({'error': 'forbidden'}), status=403, mimetype='application/json')
        img_b64 = post.get('img')
        caption = post.get('caption')
        if not img_b64:
            return {'error': 'no_image'}
        img_rec = request.env['dumuc.listing.image'].sudo().create({
            'listing_id': rec.id,
            'image': img_b64,
            'caption': caption or '',
        })
        return {'id': img_rec.id}

    # private: mark as sold
    @http.route(['/dumuc/api/seller/listing/<int:listing_id>/mark_sold'], type='json', auth='user', methods=['POST'], csrf=False)
    def api_seller_mark_sold(self, listing_id, **post):
        rec = request.env['dumuc.listing'].sudo().browse(int(listing_id))
        if not rec.exists() or rec.partner_id.id != request.env.user.partner_id.id:
            return Response(json.dumps({'error': 'forbidden'}), status=403, mimetype='application/json')
        rec.sudo().action_mark_as_sold()
        return {'status': 'ok'}
