from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError


class Diseases(models.Model):
    _name = 'disease.disease'
    _description = 'Table contains all diseases'

    name = fields.Char(string='Name', required=True)

    
    
    
    