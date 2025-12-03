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
    payment_status = fields.Selection(
        [
            ('paid', 'Paid'),
            ('unpaid', 'Unpaid'),
        ],
        string='Payment Status',
        compute='_compute_payment_status',
        store=True
    )
    notes = fields.Text(string='Notes')

    @api.depends('amount', 'amount')
    def _compute_payment_status(self):
        for record in self:
            if record.amount and record.amount > 0:
                record.payment_status = 'paid'
            else:
                record.payment_status = 'unpaid'
