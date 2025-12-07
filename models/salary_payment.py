from odoo import models, fields, api
from datetime import datetime

class PoultrySalary(models.Model):
    _name = 'salary.payment'
    _description = 'Employee Salary Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(
        'poultry.employee', string='Employee', required=True
    )
    salary_date = fields.Date(string='Salary Date', required=True)
    amount_received = fields.Monetary(string='Amount Received', required=True, default=0)
    amount_remaining = fields.Monetary(
        string='Amount Remaining',
        compute='_compute_amount_remaining',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id.id
    )
    total_salary = fields.Monetary(
        string='Total Salary',
        related='employee_id.salary',
        store=True
    )
    previous_paid_amount = fields.Monetary(
        string="Paid This Month",
        compute="_compute_previous_paid_amount",
        currency_field="currency_id",
        store=False
    )

    remaining_salary_before_payment = fields.Monetary(
        string='Remaining Before Payment',
        compute='_compute_previous_paid_amount',
        store=True,
        currency_field='currency_id'
    )
    payment_status = fields.Selection(
        [
            ('not_paid', 'Not Paid'),
            ('partially_paid', 'Partially Paid'),
            ('paid', 'Paid'),
        ],
        string='Payment Status',
        compute='_compute_payment_status',
        store=True
    )
    notes = fields.Text(string='Notes')

    @api.depends('employee_id', 'salary_date')
    def _compute_previous_paid_amount(self):
        for rec in self:
            if not rec.employee_id or not rec.salary_date:
                rec.previous_paid_amount = 0
                rec.remaining_salary_before_payment = rec.employee_id.salary if rec.employee_id else 0
                continue

            salary_month = rec.salary_date.month
            salary_year = rec.salary_date.year

            previous_payments = self.env['salary.payment'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('id', '!=', rec.id),
                ('salary_date', '>=', f"{salary_year}-{salary_month}-01"),
                ('salary_date', '<=', f"{salary_year}-{salary_month}-31"),
            ])

            total_paid = sum(previous_payments.mapped('amount_received'))

            rec.previous_paid_amount = total_paid

            rec.remaining_salary_before_payment = max(
                rec.employee_id.salary - total_paid,
                0
            )

    @api.depends('total_salary', 'amount_received')
    def _compute_payment_status(self):
        for rec in self:
            if rec.amount_received <= 0:
                rec.payment_status = 'not_paid'
            elif rec.amount_received < rec.total_salary:
                rec.payment_status = 'partially_paid'
            else:
                rec.payment_status = 'paid'
