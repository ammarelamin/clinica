# -*- coding: utf-8 -*-
# from odoo import http


# class Clinica(http.Controller):
#     @http.route('/clinica/clinica/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/clinica/clinica/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('clinica.listing', {
#             'root': '/clinica/clinica',
#             'objects': http.request.env['clinica.clinica'].search([]),
#         })

#     @http.route('/clinica/clinica/objects/<model("clinica.clinica"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('clinica.object', {
#             'object': obj
#         })
