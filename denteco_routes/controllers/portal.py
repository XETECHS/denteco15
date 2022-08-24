 # -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import http, _, fields
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal
 
class CustomerPortalExtend(CustomerPortal):
    @http.route(['/tracking_route/<int:tracking_line_id>'], type='http', auth="public", website=True)
    def portal_tracking_route(self, tracking_line_id, access_token=None, **kw):
        try:
            tracking_line_sudo = self._document_check_access('sale.route.tracking.line', tracking_line_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'tracking': tracking_line_sudo,
            'token': access_token,
            'action': tracking_line_sudo._get_portal_return_action(),
        }

        return request.render('denteco_routes.tracking_line_portal_template', values)


    @http.route(['/tracking_route/<int:tracking_line_id>/accept'], type='json', auth="public", website=True)
    def portal_tracking_route_accept(self, tracking_line_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            tracking_line_sudo = self._document_check_access('sale.route.tracking.line', tracking_line_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid tracking.')}

        try:
            tracking_line_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        tracking_line_sudo.action_confirm()

        return {
            'force_refresh': True,
            'redirect_url': tracking_line_sudo.get_portal_url(),
        }