from odoo import models, fields, api

class PoultryCustomer(models.Model):
    _name = 'poultry.customer'
    _description = 'Poultry Customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Customer Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')

    # Link all sales
    sale_ids = fields.One2many('poultry.sale', 'customer_id', string='Sales')

    # Computed fields
    total_sale = fields.Monetary(string='Total Sale', currency_field='currency_id', compute='_compute_totals', store=True)
    total_paid = fields.Monetary(string='Total Paid', currency_field='currency_id', compute='_compute_totals', store=True)
    debt = fields.Monetary(string='Total Debt', currency_field='currency_id', compute='_compute_totals', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    payment_ids = fields.One2many('poultry.payment', 'customer_id', string='Payments')

    @api.depends('sale_ids', 'sale_ids.amount_paid', 'sale_ids.amount_due')
    def _compute_totals(self):
        for customer in self:
            customer.total_sale = sum(customer.sale_ids.mapped('revenue'))
            customer.total_paid = sum(customer.sale_ids.mapped('amount_paid'))
            customer.debt = sum(customer.sale_ids.mapped('amount_due'))

    def action_register_payment(self):
        return {
            'name': 'Register Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'poultry.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_customer_id': self.id,
            }
        }

