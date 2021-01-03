from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError



class clinicLab(models.Model):
    _name = 'clinic.lab'
    _description = 'This model handles lab requests'
    _order = 'date desc'

    state = fields.Selection(string='State', selection=[('draft', 'Request'), ('invoicing', 'Invoicing'), ('progress', 'In Progress'),('done', 'Done'),('reject', 'Rejected'),],
    readonly=True, default='draft')
    name = fields.Char(string='Request', readonly=True, copy=False, default='New')
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
    test_ids = fields.One2many(comodel_name='test.line', inverse_name='line_id', string='')
    invoice_count = fields.Integer(string='Invoices', readonly=True)
    invoice_id = fields.Many2one(comodel_name='account.move', string='', readonly=True)


    @api.model
    def create(self, vals):
        if not vals.get('test_ids'):
            raise UserError("Please add tests!")
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('clinic.lab') or 'New'
            result = super(clinicLab, self).create(vals)
        return result
    

    def get_date(self,datetime):
        return datetime.date()


    @api.depends('test_ids')
    def compute_total_price(self):
        for rec in self:
            price_sum = 0
            for record in rec.test_ids:
                price_sum += record.price
            rec.price_total = price_sum


    def create_invoice(self):
        line_ids = []
        for rec in self:
            for line in rec.test_ids:
                line_ids.append({
                    'name': line.product_id.name,
                    'credit': rec.price_total,
                    'quantity': 1.0,
                    'price_unit': line.price,
                })

            invoice = self.env['account.move'].create({
                'partner_id': rec.patient_id.id,
                'ref': rec.name,
                'date': rec.date,
                'type': 'out_invoice',
                'invoice_line_ids': line_ids,
            })

            rec.write({
                'state':'invoicing',
                'invoice_id': invoice.id,
                'invoice_count': rec.invoice_count + 1,
                })


    def labrotary_payment(self):
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
                    'You cannot delete a laboratory request which is not draft!'
                )
        return super(clinicLab, self).unlink()
    


class testLine(models.Model):
    _name = 'test.line'
    _description = 'test line'

    line_id = fields.Many2one(comodel_name='clinic.lab', string='')
    state = fields.Selection(string='State', related='line_id.state', selection=[('draft', 'Request'), ('invoicing', 'Invoicing'), ('progress', 'In Progress'),('done', 'Done'),('reject', 'Rejected'),],
    readonly=False)
    product_id = fields.Many2one(comodel_name='product.template', string='Test', 
    domain=[('type','=','test')], required=True)
    test_type = fields.Selection(string='Type', selection=[('clinical_chemistry', 'Clinical Chemistry'), ('rapid_test', 'Rapid Tests'),
                                                            ('serum_lithium','Serum Lithium'),('hormons_tumor_markees','Homrmons & Tumor Markees'),
                                                            ('haematology','Haematology'), ('other','Other')],
                                                            related='product_id.test_type', store=True, readonly=False)
    price = fields.Float(string='Price', related='product_id.list_price', readonly=False)
    normal = fields.Char(string='Normal', related='product_id.normal', readonly=False)
    result = fields.Char(string='Result')
    situation = fields.Selection(string='Situation', selection=[('positive', 'Positive'), ('negative', 'Negative'),
                                                                ('normal', 'Normal'),])
