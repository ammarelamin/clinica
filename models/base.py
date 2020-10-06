from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError




class resPartner(models.Model):
    _inherit = 'res.partner'

    patientID = fields.Char(string='Patient ID', readonly=True, copy=False, default='New')
    address_name = fields.Char(string='Address')
    is_patient = fields.Boolean(string='Is Patient?', default=True)
    date_of_birth = fields.Date(string='Date Of Birth', required=False)
    age = fields.Integer(string='Age', required=False)
    gender = fields.Selection(string='Gender', selection=[('male', 'Male'), ('female', 'Female'),],
    default='female')
    company_type = fields.Selection(default='person')
    gender = fields.Selection(string='Gender', selection=[('male', 'Male'), ('female', 'Female'),],
    default='female')
    appointments = fields.Integer(string='Appointments',readonly=True, compute='patient_history')
    tests_count = fields.Integer(string='Laboratory',readonly=True, compute='laboratory_history')
    disease_ids = fields.Many2many(comodel_name='disease.disease', string='Diseases')
    
    
    @api.model
    def create(self, vals):
        if vals.get('patientID', 'New') == 'New':
            vals['patientID'] = self.env['ir.sequence'].next_by_code('res.partner') or ''
            result = super(resPartner, self).create(vals)
        return result

    
    @api.constrains('age')
    def check_age(self):
        for record in self:
            if record.age == 0:
                raise ValidationError("Please enter valid age!")
    
    
    def patient_history(self):
        self.ensure_one()
        history_list = []
        for rec in self:
            history_count = self.env['calendar.event'].search_count([('patient_id','=',rec.id)])
            history_ids = self.env['calendar.event'].search([('patient_id','=',rec.id)])
            history_list = history_ids.mapped('id')
            rec.write({'appointments': history_count})

        return {
        'name': 'Appointments',
        'type': 'ir.actions.act_window',
        'view_mode': 'tree,form',
        'res_model': 'calendar.event',
        'view_id': False,
        'target': 'current',
        'domain': [('id','in', history_list)],
        'context': {'default_patient_id': self.id},
        }

    
        
    def laboratory_history(self):
        self.ensure_one()
        lab_list = []
        for rec in self:
            history_count = self.env['clinic.lab'].search_count([('patient_id','=',rec.id)])
            lab_ids = self.env['clinic.lab'].search([('patient_id','=',rec.id)])
            lab_list = lab_ids.mapped('id')
            rec.write({'tests_count': history_count})

        return {
        'name': 'Laboratory Tests',
        'type': 'ir.actions.act_window',
        'view_mode': 'tree,form',
        'res_model': 'clinic.lab',
        'domain': [('id','in', lab_list)],
        'context': {'default_patient_id': self.id},
        }


class calendarEvent(models.Model):
    _inherit = 'calendar.event'

    state = fields.Selection(string='State', selection=[('draft', 'Draft'), ('invoicing', 'Invoicing'), ('progress', 'In Progress'),('done', 'Done'),],
    readonly=True, default='draft')
    name = fields.Char(string='Appointment Subject')
    partner_ids = fields.Many2many(comodel_name='res.partner', string='Patient', domain=[('is_patient','=',False)])
    patient_id = fields.Many2one(comodel_name='res.partner', required=True, domain=[('is_patient','=',True)])
    patientID = fields.Char(string='Patient ID', related='patient_id.patientID')
    age = fields.Integer(string='Age', related='patient_id.age')
    gender = fields.Selection(string='Gender', selection=[('male', 'Male'), ('female', 'Female'),],
    related='patient_id.gender')
    product_id = fields.Many2one(comodel_name='product.template', string='Service', 
    domain=[('type','=','service')], required=True)
    note = fields.Text(string='Note')
    user_id = fields.Many2one(string='Responsible', readonly=True)
    invoices = fields.Integer(string='Invoices', readonly=True)
    invoice_id = fields.Many2one(comodel_name='account.move', string='', readonly=True)
    

    def get_date(self,datetime):
        return datetime.date()
    

    def create_invoice(self):
        product_list = []      
        for rec in self:
            product_list.append({
                'product_id': rec.product_id.id,
                'name': rec.product_id.name,
                'credit': rec.product_id.list_price,
                'account_id': rec.product_id.categ_id.property_account_income_categ_id.id,
                'quantity': 1.0,
                'price_unit': rec.product_id.list_price,
            })
            invoice = self.env['account.move'].create({
                'partner_id': rec.patient_id.id,
                'date': rec.get_date(rec.start_datetime),
                'amount_total': rec.product_id.list_price,
                'type': 'out_invoice',
                'invoice_line_ids': product_list,
            })
            rec.write({'invoices': rec.invoices + 1,
                'state':'invoicing',
                'invoice_id': invoice.id
                })


    def appointment_invoices(self):
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('type', '=', 'out_invoice'),('id','=',self.invoice_id.id)],
            'target': 'current',
            }

    
    def appointment_payment(self):
        for rec in self:
            if rec.invoice_id.invoice_payment_state == 'paid':
                rec.write({'state':'progress'})
            else:
                raise ValidationError("Plaese register the payment first")
            
    
    def appointment_done(self):
        self.write({'state':'done'})



class productTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(selection=[('consu', 'Consumable'), ('service', 'Service'), ('test', 'Laboratory Test'), ('product', 'Stockable Product'),])
    normal = fields.Char(string='Normal')
    test_type = fields.Selection(string='Type', selection=[('clinical_chemistry', 'Clinical Chemistry'), ('rapid_test', 'Rapid Tests'),
                                                            ('serum_lithium','Serum Lithium'),('hormons_tumor_markees','Homrmons & Tumor Markees'),
                                                            ('haematology','Haematology'), ('other','Other')])
