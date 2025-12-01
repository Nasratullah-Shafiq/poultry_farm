from odoo import models, fields, api

class PoultrySalary(models.Model):
    _name = 'salary.payment'
    _description = 'Employee Salary Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(
        'poultry.employee', string='Employee', required=True
    )
    salary_date = fields.Date(string='Salary Date', required=True)
    amount = fields.Monetary(string='Amount', required=True)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id.id
    )
    notes = fields.Text(string='Notes')
