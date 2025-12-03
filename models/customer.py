from odoo import models, fields, api


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
    payment_status = fields.Selection(
        [
            ('not_paid', 'Not Paid'),
            ('partial', 'Partially Paid'),
            ('paid', 'Fully Paid')
        ],
        string='Payment Status',
        compute='_compute_totals',
        store=True,
        tracking=True
    )


    # --------------------------------------------------------
    # COMPUTE METHOD FOR TOTALS AND PAYMENT STATUS
    # --------------------------------------------------------
    @api.depends('total_paid', 'debt')
    def _compute_payment_status(self):
        for record in self:
            if record.debt > 0 and record.total_paid > 0:
                record.payment_status = 'partially_paid'
            elif record.debt > 0 and record.total_paid == 0:
                record.payment_status = 'not_paid'
            elif record.debt == 0:
                record.payment_status = 'fully_paid'
            else:
                record.payment_status = 'not_paid'  # fallback

    @api.depends('sale_ids.total', 'payment_ids.amount')
    def _compute_totals(self):
        for customer in self:
            # Sum of all sales total
            total_sale = 0.0
            for sale in customer.sale_ids:
                if sale.total:
                    total_sale += sale.total
            customer.total_sale = total_sale

            # Sum of all payments amount
            total_paid = 0.0
            for payment in customer.payment_ids:
                if payment.amount:
                    total_paid += payment.amount
            customer.total_paid = total_paid

            # Debt = total_sale - total_paid
            customer.debt = total_sale - total_paid

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

