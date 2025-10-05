# poultry_farm_management/models/employee.py
from odoo import models, fields, api
from datetime import date

class PoultryEmployee(models.Model):
    _name = 'poultry.employee'
    _description = 'Poultry Farm Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter


    name = fields.Char(required=True)
    employee_code = fields.Char()
    branch_id = fields.Many2one('poultry.branch', string='Branch')
    job_title = fields.Char()
    phone = fields.Char()
    address = fields.Text()
    hire_date = fields.Date()
    salary = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    # Attendance placeholder field: a simple counter or last sign-in
    last_attendance = fields.Datetime()
    active = fields.Boolean(default=True)

class PoultrySalaryPayment(models.Model):
    _name = 'poultry.salary'
    _description = 'Employee Salary Payment'

    employee_id = fields.Many2one('poultry.employee', required=True)
    amount = fields.Monetary(currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    payment_date = fields.Date(default=fields.Date.context_today)
    journal_id = fields.Many2one('account.journal', string='Journal')
    note = fields.Text()
