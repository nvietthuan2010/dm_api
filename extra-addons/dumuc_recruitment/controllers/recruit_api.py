# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json
from recruit_jwt import create_access_token, create_refresh_token, decode_token
from credit_guard import require_credit

def json_response(data=None, message=None, success=True, status=200):
    res = {
        "success": success,
        "message": message,
        "data": data
    }
    return Response(
        json.dumps(res, ensure_ascii=False),
        status=status,
        mimetype='application/json'
    )

def paginate(env_model, domain, page=1, limit=20, fields=None):
    offset = (page - 1) * limit
    total = env_model.search_count(domain)
    records = env_model.search(domain, offset=offset, limit=limit)

    if fields:
        data = records.read(fields)
    else:
        data = [r.id for r in records]

    return {
        "paging": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total // limit) + (1 if total % limit else 0)
        },
        "data": data
    }



class RecruitAPI(http.Controller):
    def _cors(self, response):
        response.headers['Access-Control-Allow-Origin'] = "https://yourdomain.com"
        response.headers['Access-Control-Allow-Methods'] = "GET, POST, PUT, OPTIONS"
        response.headers['Access-Control-Allow-Headers'] = "Authorization, Content-Type"
        return response
    # Helper: Auth via Header "Authorization: Bearer <token>"
    def _jwt_auth(self, required_role=None):
        header = request.httprequest.headers.get("Authorization")
        if not header or not header.startswith("Bearer "):
            return None

        token = header.replace("Bearer ", "")

        try:
            payload = decode_token(token)
            if payload.get('type') != 'access':
                return None
        except Exception:
            return None

        # Validate scope
        if payload.get('scope') != 'recruitment':
            return None

        user_id = payload.get("sub")
        jwt_role = payload.get("role")

        # role check
        if required_role and jwt_role != required_role:
            return None
        if request.env['jwt.blacklist'].sudo().search([('jti', '=', payload['jti'])], limit=1):
            return None


        user = request.env['res.users'].sudo().browse(user_id)
        return user if user.exists() else None




    ##################################
    # AUTH
    ##################################

    # Route: POST /api/recruit/auth/login
    # Description: Public login, return token for authenticated requests.
    @http.route('/api/recruit/auth/login', type='json', auth='public', methods=['POST'], csrf=False)
    def login(self, **kw):
        email = kw.get('email')
        password = kw.get('password')

        user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if not user:
            return json_response(success=False, message="Không tồn tại tài khoản.", status=401)

        if not user._check_password(password):
            return json_response(success=False, message="Sai mật khẩu.", status=401)

        if user.has_group('dumuc_recruitment.group_recruitment_admin'):
            role = 'admin'
        elif user.has_group('dumuc_recruitment.group_recruitment_employer'):
            role = 'employer'
        elif user.has_group('dumuc_recruitment.group_recruitment_seeker'):
            role = 'seeker'
        else:
            role = 'guest'
        
        access = create_access_token(user.id, role)
        refresh = create_refresh_token(user.id)

        # Store Refresh Token hashed
        user.sudo().write({
            'jwt_refresh_token': refresh
        })

        return json_response({
            "access_token": access,
            "refresh_token": refresh,
            "user_id": user.id,
            "name": user.name
        }, "Đăng nhập thành công")


    @http.route('/api/recruit/auth/refresh', type='json', auth='public', methods=['POST'], csrf=False)
    def refresh(self, **kw):
        refresh = kw.get('refresh_token')
        if not refresh:
            return json_response(success=False, message="Thiếu token.", status=400)

        try:
            payload = decode_token(refresh)
            if payload.get('type') != 'refresh':
                return json_response(success=False, message="Token không hợp lệ.", status=401)
        except Exception:
            return json_response(success=False, message="Token hết hạn hoặc sai.", status=401)

        user = request.env['res.users'].sudo().browse(payload.get('sub'))
        if not user or user.jwt_refresh_token != refresh:
            return json_response(success=False, message="Token không khớp hệ thống.", status=401)

        new_access = create_access_token(user.id)

        return json_response({
            "access_token": new_access
        }, "Cấp token thành công")

    @http.route('/api/recruit/auth/logout', type='json', auth='public', methods=['POST'], csrf=False)
    def logout(self, **kw):
        token = request.httprequest.headers.get("Authorization").replace("Bearer ", "")
        payload = decode_token(token)

        request.env['jwt.blacklist'].sudo().create({"jti": payload['jti']})

        return json_response(message="Đã logout.", success=True)


    ##################################
    # PUBLIC JOB API
    ##################################

    # Route: GET /api/recruit/job/list
    # Description: Public job listing, only returns active jobs.
    @http.route('/api/recruit/job/list', auth='public', type='http', methods=['GET'], csrf=False)
    def list_jobs(self, **kw):
        page = int(kw.get('page', 1))
        limit = int(kw.get('limit', 20))

        domain = [('status', '=', 'active')]

        if kw.get('category'):
            domain.append(('category_id', '=', int(kw['category'])))

        if kw.get('location'):
            domain.append(('location', 'ilike', kw['location']))

        if kw.get('employment'):
            domain.append(('employment_type', '=', kw['employment']))

        if kw.get('urgent'):
            val = kw['urgent'].lower() in ['1', 'true', 'yes']
            domain.append(('is_urgent', '=', val))

        if kw.get('salary_min'):
            domain.append(('salary_min', '>=', int(kw['salary_min'])))

        if kw.get('salary_max'):
            domain.append(('salary_max', '<=', int(kw['salary_max'])))

        if kw.get('keyword'):
            keyword = kw['keyword']
            domain += ['|', ('title', 'ilike', keyword), ('description', 'ilike', keyword)]

        result = paginate(request.env['dumuc.job'].sudo(), domain, page, limit, fields=[
            'id', 'title', 'location', 'salary_min', 'salary_max', 'company_id', 'category_id'
        ])

        return json_response(data=result['data'], message="ok", success=True, status=200)


    @http.route('/api/recruit/docs', auth='public', type='http', methods=['GET'], csrf=False)
    def docs(self):
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "DUMUC Recruit API",
                "version": "1.0.0"
            },
            "paths": {
                "/api/recruit/job/list": {
                    "get": {
                        "summary": "Danh sách tin tuyển dụng",
                        "parameters": [
                            {"name": "page", "in": "query", "schema": {"type": "integer"}},
                            {"name": "limit", "in": "query", "schema": {"type": "integer"}},
                            {"name": "category", "in": "query"},
                            {"name": "location", "in": "query"},
                            {"name": "keyword", "in": "query"}
                        ],
                        "responses": {
                            "200": {"description": "OK"}
                        }
                    }
                },
                "/api/recruit/auth/login": {
                    "post": {
                        "summary": "Login lấy token",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        return Response(
            json.dumps(spec, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )



    # Route: GET /api/recruit/job/detail/<id>
    # Description: Public get job detail.
    @http.route('/api/recruit/job/detail/<int:job_id>', auth='public', type='http', methods=['GET'], csrf=False)
    def job_detail(self, job_id):
        job = request.env['dumuc.job'].sudo().browse(job_id)
        if not job or job.status != 'active':
            return json_response(success=False, message="Tin tuyển dụng không tồn tại.", status=404)

        return json_response({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "location": job.location,
            "company": job.company_id.name,
        })


    ##################################
    # EMPLOYER JOB
    ##################################

    # Route: POST /api/recruit/job/create
    # Description: Employer tạo job trạng thái nháp.
    @http.route('/api/recruit/job/create', auth='public', type='json', methods=['POST'], csrf=False)
    @require_credit("POST_JOB")
    def create_job(self, **kw):
        user = self._jwt_auth()
        if not user:
            return json_response(success=False, message="Không có quyền.", status=401)

        company = user.company_id

        vals = {
            "title": kw.get('title'),
            "description": kw.get('description'),
            "salary_min": kw.get('salary_min'),
            "salary_max": kw.get('salary_max'),
            "category_id": kw.get('category_id'),
            "company_id": company.id,
            "status": "draft",
        }

        job = request.env['dumuc.job'].sudo().create(vals)

        return json_response({"job_id": job.id, "status": job.status}, "Tạo tin thành công.")


    # Route: POST /api/recruit/job/submit
    # Description: Employer submit job for approval.
    @http.route('/api/recruit/job/submit', auth='public', type='json', methods=['POST'], csrf=False)
    def submit_job(self, **kw):
        user = self._jwt_auth()
        if not user:
            return json_response(success=False, message="Không có quyền.", status=401)

        job = request.env['dumuc.job'].sudo().browse(kw.get('job_id'))

        try:
            job.action_submit()
        except Exception as e:
            return json_response(success=False, message=str(e), status=400)

        return json_response({"status": job.status}, "Đã gửi duyệt.")


    # Route: POST /api/recruit/job/update
    # Description: Employer update draft/rejected job only.
    @http.route('/api/recruit/job/update', type='json', auth='public', methods=['POST'], csrf=False)
    def update_job(self, **kw):
        user = self._jwt_auth()
        if not user:
            return json_response(success=False, message="Không có quyền.", status=401)

        job = request.env['dumuc.job'].sudo().browse(kw.get('job_id'))

        if job.status not in ['draft', 'rejected']:
            return json_response(success=False, message="Chỉ cập nhật tin Nháp / Bị từ chối.", status=400)

        allowed = ['title', 'description', 'salary_min', 'salary_max', 'category_id', 'employment_type', 'location']
        vals = {k: v for k, v in kw.items() if k in allowed}

        job.write(vals)

        return json_response({"id": job.id, "status": job.status}, "Cập nhật thành công.")


    # Route: GET /api/recruit/employer/job/my
    # Description: View all jobs created by employer.
    @http.route('/api/recruit/employer/job/my', type='http', auth='public', methods=['GET'], csrf=False)
    def employer_job_my(self):
        user = self._jwt_auth()
        if not user:
            return json_response(success=False, message="Không có quyền.", status=401)

        company = user.company_id
        jobs = request.env['dumuc.job'].sudo().search([('company_id', '=', company.id)])

        data = [{
            "id": j.id,
            "title": j.title,
            "status": j.status,
        } for j in jobs]

        return json_response(data)


    ##################################
    # ADMIN JOB APPROVAL
    ##################################

    # Route: POST /api/recruit/admin/job/approve
    # Description: Admin approve pending job.
    @http.route('/api/recruit/admin/job/approve', auth='public', type='json', methods=['POST'], csrf=False)
    def approve_job(self, **kw):
        user = self._jwt_auth()
        if not user or not user.has_group('dumuc_recruitment.group_recruitment_admin'):
            return json_response(success=False, message="Không đủ quyền.", status=403)

        job = request.env['dumuc.job'].sudo().browse(kw.get('job_id'))

        try:
            job.action_approve()
        except Exception as e:
            return json_response(success=False, message=str(e), status=400)

        return json_response({"status": job.status}, "Duyệt tin thành công.")


    ##################################
    # APPLICATION
    ##################################

    # Route: POST /api/recruit/application/apply
    # Description: Seeker apply job.
    @http.route('/api/recruit/application/apply', auth='public', type='json', methods=['POST'], csrf=False)
    def apply(self, **kw):
        user = self._jwt_auth()
        if not user or not user.has_group('dumuc_recruitment.group_recruitment_seeker'):
            return json_response(success=False, message="Không đủ quyền.", status=403)

        vals = {
            "job_id": kw.get("job_id"),
            "seeker_id": user.seeker_id.id,
            "cover_letter": kw.get("cover_letter"),
        }

        try:
            app = request.env['dumuc.application'].sudo().create(vals)
        except Exception as e:
            return json_response(success=False, message=str(e), status=400)

        return json_response({"application_id": app.id}, "Ứng tuyển thành công.")


    # Route: GET /api/recruit/job/<id>/applicants
    # Description: Employer view applicants for their job.
    @http.route('/api/recruit/job/<int:job_id>/applicants', type='http', auth='public', methods=['GET'], csrf=False)
    def job_applicants(self, job_id):
        user = self._jwt_auth()
        if not user:
            return json_response(success=False, message="Không có quyền.", status=401)

        job = request.env['dumuc.job'].sudo().browse(job_id)
        if job.company_id != user.company_id:
            return json_response(success=False, message="Không được xem ứng viên tin của Garage khác.", status=403)

        applicants = request.env['dumuc.application'].sudo().search([('job_id', '=', job.id)])

        data = []
        for app in applicants:
            seeker = app.seeker_id
            unlocked = user.company_id in seeker.phone_unlocked_by
            data.append({
                "application_id": app.id,
                "seeker": seeker.full_name,
                "headline": seeker.headline,
                "status": app.status,
                "phone": seeker.phone if unlocked else None,
                "unlocked": unlocked
            })

        return json_response(data)


    # Route: GET /api/recruit/seeker/application/my
    # Description: Seeker view their applications.
    @http.route('/api/recruit/seeker/application/my', type='http', auth='public', methods=['GET'], csrf=False)
    def seeker_app_my(self):
        user = self._jwt_auth()
        if not user:
            return json_response(success=False, message="Không có quyền.", status=401)

        seeker = user.seeker_id
        apps = request.env['dumuc.application'].sudo().search([('seeker_id', '=', seeker.id)])

        data = [{
            "application_id": a.id,
            "job_id": a.job_id.id,
            "job_title": a.job_id.title,
            "status": a.status,
        } for a in apps]

        return json_response(data)


    ##################################
    # SEEKER PROFILE
    ##################################

    # Route: POST /api/recruit/seeker/profile/update
    # Description: Seeker update own profile.
    @http.route('/api/recruit/seeker/profile/update', type='json', auth='public', methods=['POST'], csrf=False)
    def seeker_update(self, **kw):
        user = self._jwt_auth()
        if not user:
            return json_response(success=False, message="Không có quyền.", status=401)

        seeker = user.seeker_id
        allowed = ['headline', 'exp_years', 'skills', 'location']

        vals = {k: v for k, v in kw.items() if k in allowed}
        seeker.write(vals)

        return json_response({"seeker_id": seeker.id}, "Cập nhật hồ sơ thành công.")


    @http.route('/api/seeker/<int:seeker_id>/unlock', type='json', auth='public', methods=['POST'], csrf=False)
    @jwt_required
    @require_credit("VIEW_SEEKER")
    def unlock_seeker(self, seeker_id, **kwargs):

        company = request.env.company
        env = request.env

        # Validate seeker exists
        seeker = env['dumuc.job.seeker'].sudo().search([('id', '=', seeker_id)], limit=1)
        if not seeker:
            return {"status": "error", "message": "Ứng viên không tồn tại"}

        # Check duplicate unlock
        unlock = env['dumuc.seeker.unlock'].sudo().search([
            ('company_id', '=', company.id),
            ('seeker_id', '=', seeker_id)
        ], limit=1)

        if unlock:
            return {
                "status": "already_unlocked",
                "message": "Ứng viên đã được mở khóa trước đó",
                "credit_used": False,
                "seeker": {
                    "id": seeker.id,
                    "full_name": seeker.full_name,
                    "phone": seeker.phone,
                    "email": seeker.email
                }
            }

        # credit consumption executed by require_credit decorator

        # Create unlock record
        env['dumuc.seeker.unlock'].sudo().create({
            'company_id': company.id,
            'seeker_id': seeker.id
        })

        # Success response
        return {
            "status": "success",
            "message": "Mở khóa thành công ứng viên",
            "credit_used": True,
            "seeker": {
                "id": seeker.id,
                "full_name": seeker.full_name,
                "phone": seeker.phone,
                "email": seeker.email
            }
        }

    ##################################
    # CREDIT
    ##################################

    # Route: GET /api/recruit/credit/balance
    # Description: Employer view credit balance.
    @http.route('/api/recruit/credit/balance', auth='public', type='http', methods=['GET'], csrf=False)
    def credit_balance(self):
        user = self._jwt_auth()
        if not user:
            return json_response(success=False, message="Không có quyền.", status=401)

        company = user.company_id
        return json_response({"balance": company.credit_balance})


    # Route: POST /api/recruit/credit/topup
    # Description: Employer manual credit topup (for testing).
    @http.route('/api/recruit/credit/topup', type='json', auth='public', methods=['POST'], csrf=False)
    def credit_topup(self, **kw):
        user = self._jwt_auth()
        if not user:
            return json_response(success=False, message="Không có quyền.", status=401)

        company = user.company_id
        amount = kw.get("credits")

        if not amount or amount <= 0:
            return json_response(success=False, message="Số credit không hợp lệ.", status=400)

        new_balance = company.credit_balance + amount

        request.env['dumuc.credit.transaction'].sudo().create({
            'company_id': company.id,
            'type': 'topup',
            'amount': amount,
            'balance_after': new_balance,
            'description': "Nạp credit (API demo)"
        })

        return json_response({"balance": new_balance}, "Nạp credit thành công.")


    ##################################
    # COMPANY
    ##################################

    # Route: GET /api/recruit/company/my
    # Description: Employer view their company profile.
    @http.route('/api/recruit/company/my', type='http', auth='public', methods=['GET'], csrf=False)
    def company_my(self):
        user = self._jwt_auth()
        if not user:
            return json_response(success=False, message="Không có quyền.", status=401)

        comp = user.company_id
        return json_response({
            "id": comp.id,
            "name": comp.name,
            "verify_status": comp.verify_status,
            "credit_balance": comp.credit_balance
        })


    ##################################
    # ADMIN COMPANY VERIFY
    ##################################

    # Route: GET /api/recruit/admin/company/pending
    # Description: Admin view pending companies.
    @http.route('/api/recruit/admin/company/pending', type='http', auth='public', methods=['GET'], csrf=False)
    def admin_company_pending(self):
        user = self._jwt_auth()
        if not user or not user.has_group('dumuc_recruitment.group_recruitment_admin'):
            return json_response(success=False, message="Không đủ quyền.", status=403)

        comps = request.env['dumuc.company'].sudo().search([('verify_status', '=', 'pending')])

        return json_response([{
            "id": c.id,
            "name": c.name
        } for c in comps])


    # Route: POST /api/recruit/admin/company/verify
    # Description: Admin verify company.
    @http.route('/api/recruit/admin/company/verify', type='json', auth='public', methods=['POST'], csrf=False)
    def admin_company_verify(self, **kw):
        user = self._jwt_auth()
        if not user or not user.has_group('dumuc_recruitment.group_recruitment_admin'):
            return json_response(success=False, message="Không đủ quyền.", status=403)

        comp = request.env['dumuc.company'].sudo().browse(kw.get('company_id'))
        comp.verify_status = 'verified'

        return json_response({"id": comp.id}, "Xác thực công ty thành công.")
