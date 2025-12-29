# poultry_farm_management/models/employee.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date

class PoultryEmployee(models.Model):
    _name = 'poultry.employee'
    _description = 'Poultry Farm Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter


    name = fields.Char(required=True)
    employee_code = fields.Char(string='Employee Code', readonly=True, copy=False)
    branch_id = fields.Many2one('poultry.branch', string='Branch', required=True)
    job_title = fields.Char(string = "Job Title", required=True)
    phone = fields.Char(string="Phone", required=True)
    address = fields.Text()
    hire_date = fields.Date(string="Date", required=True)
    salary = fields.Monetary(currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    image_1920 = fields.Image(string='Employee Photo', max_width=1920, max_height=1920)
    # currency_id = fields.Selection(
    #     [('USD', 'USD'), ('AFN', 'Afghani'), ('KLD', 'Kaldar')],
    #     string='Currency',
    #     default='AFN'
    # )
    # Attendance placeholder field: a simple counter or last sign-in
    last_attendance = fields.Datetime()
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        # Generate employee_code only if not set
        if not vals.get('employee_code'):
            # Get the last created employee_code numeric part globally
            last_employee = self.search([('employee_code', '!=', False)], order='id desc', limit=1)
            if last_employee and last_employee.employee_code and '-' in last_employee.employee_code:
                try:
                    last_number = int(last_employee.employee_code.split('-')[1])
                except:
                    last_number = 0
                new_number = str(last_number + 1).zfill(3)
            else:
                new_number = '001'

            # Use first 3 letters of name as prefix
            prefix = vals.get('name', 'EMP').replace(' ', '').upper()[:3]
            vals['employee_code'] = f'{prefix}-{new_number}'

        return super(PoultryEmployee, self).create(vals)

    def write(self, vals):
        for rec in self:
            # Only generate employee_code if not already set
            if not rec.employee_code and vals.get('name'):
                last_employee = self.search([('employee_code', '!=', False)], order='id desc', limit=1)
                if last_employee and last_employee.employee_code and '-' in last_employee.employee_code:
                    try:
                        last_number = int(last_employee.employee_code.split('-')[1])
                    except:
                        last_number = 0
                    new_number = str(last_number + 1).zfill(3)
                else:
                    new_number = '001'

                prefix = vals.get('name', 'EMP').replace(' ', '').upper()[:3]
                vals['employee_code'] = f'{prefix}-{new_number}'

        return super(PoultryEmployee, self).write(vals)


