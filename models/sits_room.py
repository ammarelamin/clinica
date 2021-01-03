from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class Sits(models.Model):
    _name = 'sit.sit'
    _description = 'Model for sits management'

    state = fields.Selection(string='State', selection=[('draft', 'Request'), ('invoicing', 'Invoicing'), ('progress', 'In Progress'),('done', 'Done'),('reject', 'Rejected'),],
    readonly=True, default='draft')
    name = fields.Char(string='SIT', readonly=True, copy=False, default='New')
    date = fields.Datetime(string='Date', default=fields.Datetime.now,
    required=True)
    patient_id = fields.Many2one(comodel_name='res.partner', string='Patient Name',
    required=True, domain=[('is_patient','=',True)])
    patientID = fields.Char(string='Patient ID', related='patient_id.patientID',
    readonly=True)
    patient_age = fields.Integer(string='Age', related='patient_id.age',
    readonly=True)
    price_total = fields.Float(string='Total', compute='compute_total_price', store=True)
    note = fields.Text(string='Note')
    user_id = fields.Many2one(comodel_name='res.users', string='Responsible', readonly=True,
    default=lambda self: self.env.user)
    sit_ids = fields.One2many(comodel_name='sit.line', inverse_name='line_id', string='')
    invoice_id = fields.Many2one(comodel_name='account.move', string='', readonly=True)
    invoice_count = fields.Integer(string='Invoices', readonly=True)
    


    @api.model
    def create(self, vals):
        if not vals.get('sit_ids'):
            raise ValidationError("No sits were added!")
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sit.sit') or 'New'
            result = super(Sits, self).create(vals)
        return result


    @api.depends('sit_ids')
    def compute_total_price(self):
        for rec in self:
            price_sum = 0
            for record in rec.sit_ids:
                price_sum += record.price
            rec.price_total = price_sum



    def create_invoice(self):
        line_ids = []
        for rec in self:
            for line in rec.sit_ids:
                line_ids.append({
                    'name': line.product_id.name,
                    'credit': rec.price_total,
                    'quantity': 1.0,
                    'price_unit': line.product_id.list_price,
                })

            invoice = self.env['account.move'].create({
                'partner_id': rec.patient_id.id,
                'ref': rec.name,
                'invoice_date': rec.date,
                'type': 'out_invoice',
                'invoice_line_ids': line_ids,
            })

            rec.write({
                'state':'invoicing',
                'invoice_id': invoice.id,
                'invoice_count': rec.invoice_count + 1,
                })

    
    def sit_payment(self):
        for rec in self:
            if rec.invoice_id.invoice_payment_state == 'paid':
                rec.write({'state':'progress'})
            else:
                raise ValidationError("Plaese register the payment first!")
            
    
    def open_invoice(self):
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('type', '=', 'out_invoice'),('id','=',self.invoice_id.id)],
            'target': 'current',
            'context': {'create': False},
            }


    def state_done(self):
        self.write({'state':'done'})

    
    def unlink(self):
        for record in self:
            if record.state not in ('draft'):
                raise UserError(
                    'You cannot delete a sit request which is not draft!'
                )
        return super(Sits, self).unlink()



class sitLine(models.Model):
    _name = 'sit.line'
    _description = 'Sit Line'

    line_id = fields.Many2one(comodel_name='sit.sit', string='')
    state = fields.Selection(string='State', related='line_id.state', selection=[('draft', 'Request'), ('invoicing', 'Invoicing'), ('progress', 'In Progress'),('done', 'Done'),('reject', 'Rejected'),],
    readonly=True)
    product_id = fields.Many2one(comodel_name='product.template', string='Sit', 
    domain=[('type','=','service')], required=True)
    price = fields.Float(string='Price', related='product_id.list_price', readonly=False)




