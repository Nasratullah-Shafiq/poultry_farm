from odoo import models, fields, api

# class PoultryCustomer(models.Model):
#     _name = 'poultry.customer'
#     _description = 'Poultry Customer'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#
#     name = fields.Char(string='Customer Name', required=True)
#     email = fields.Char(string='Email')
#     phone = fields.Char(string='Phone')
#
#     # Link all sales
#     sale_ids = fields.One2many('poultry.sale', 'customer_id', string='Sales')
#
#     # Computed fields
#     total_sale = fields.Monetary(string='Total Sale', currency_field='currency_id', compute='_compute_totals',
#                                  store=True)
#     total_paid = fields.Monetary(string='Total Paid', currency_field='currency_id', compute='_compute_totals',
#                                  store=True)
#     debt = fields.Monetary(string='Total Debt', currency_field='currency_id', compute='_compute_totals', store=True)
#     currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
#
#     payment_ids = fields.One2many('poultry.payment', 'customer_id', string='Payments')
#
#     @api.depends(
#         'sale_ids',
#         'sale_ids.revenue',
#         'payment_ids',
#         'payment_ids.amount',
#     )
#     def _compute_totals(self):
#         for customer in self:
#             # Total sale revenue from all sales
#             customer.total_sale = sum(customer.sale_ids.mapped('revenue'))
#
#             # Total payment received
#             customer.total_paid = sum(customer.payment_ids.mapped('amount'))
#
#             # Remaining debt
#             customer.debt = customer.total_sale - customer.total_paid
#
#     def action_register_payment(self):
#         return {
#             'name': 'Register Payment',
#             'type': 'ir.actions.act_window',
#             'res_model': 'poultry.payment',
#             'view_mode': 'form',
#             'target': 'new',
#             'context': {
#                 'default_customer_id': self.id,
#             }
#         }
    # @api.depends('sale_ids.revenue', 'sale_ids.payment_ids.amount')
    # def _compute_totals(self):
    #     for customer in self:
    #         total_sale = 0.0
    #         total_paid = 0.0
    #         debt = 0.0
    #         for sale in customer.sale_ids:
    #             total_sale += sale.revenue
    #             total_paid += sum(sale.payment_ids.mapped('amount'))
    #             debt += sale.revenue - sum(sale.payment_ids.mapped('amount'))
    #         customer.total_sale = total_sale
    #         customer.total_paid = total_paid
    #         customer.debt = debt



class PoultryCustomer(models.Model):
    _name = 'poultry.customer'
    _description = 'Poultry Customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(string='Customer Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')

    # Relations
    sale_ids = fields.One2many('poultry.sale', 'customer_id', string='Sales')
    payment_ids = fields.One2many('poultry.payment', 'customer_id', string='Payments')

    # Currency
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    # Computed Totals
    total_sale = fields.Monetary(
        string='Total Sale',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )
    total_paid = fields.Monetary(
        string='Total Paid',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )
    debt = fields.Monetary(
        string='Total Debt',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )

    # Compute Totals
    @api.depends(
        'sale_ids',
        'sale_ids.amount_paid',
        'payment_ids',
        'payment_ids.amount',
    )
    def _compute_totals(self):
        for customer in self:
            # Total sale revenue
            customer.total_sale = sum(customer.sale_ids.mapped('revenue')) or 0.0

            # ----- A: PAID directly inside sale model -----
            sale_model_paid = sum(customer.sale_ids.mapped('amount_paid'))

            # ----- B: PAID from payment model -----
            payment_model_paid = sum(customer.payment_ids.mapped('amount'))

            # ----- TOTAL PAID -----
            customer.total_paid = sale_model_paid + payment_model_paid

            # ----- DEBT -----
            customer.debt = customer.total_sale - customer.total_paid

    # Wizard for Register Payment
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

