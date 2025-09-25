from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PoultrySaleReportWizard(models.TransientModel):
    _name = 'poultry.sale.report.wizard'
    _description = 'Poultry Sale Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    branch_id = fields.Many2one('poultry.branch', string="Branch")

    total_quantity = fields.Float(string="Total Quantity", readonly=True)
    total_revenue = fields.Monetary(string="Total Revenue", readonly=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, readonly=True)

    sale_lines = fields.One2many(
        'poultry.sale.report.line',
        'wizard_id',
        string="Sale Details",
        readonly=True
    )

    @api.constrains('start_date', 'end_date')
    def _check_date_range(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError("End Date cannot be earlier than Start Date.")

    def _get_domain(self):
        domain = [
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date)
        ]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        return domain

    def generate_report(self):
        """Fetch and compute sale totals and details."""
        self.ensure_one()
        domain = self._get_domain()
        Sale = self.env['poultry.sale']
        sales = Sale.search(domain, order='date asc')

        # Clear previous lines
        self.sale_lines.unlink()

        total_qty = 0
        total_revenue = 0

        for sale in sales:
            self.env['poultry.sale.report.line'].create({
                'wizard_id': self.id,
                'date': sale.date,
                'branch_id': sale.branch_id.id,
                'poultry_type_id': sale.poultry_type_id.id,
                'quantity': sale.quantity,
                'unit_price': sale.unit_price,
                'revenue': sale.revenue,
                'buyer': sale.buyer,
            })
            total_qty += sale.quantity
            total_revenue += sale.revenue

        self.total_quantity = total_qty
        self.total_revenue = total_revenue

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'poultry.sale.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def print_pdf_report(self):
        self.generate_report()
        return self.env.ref('poultry_farm.action_poultry_sale_report').report_action(self)


class PoultrySaleReportLine(models.TransientModel):
    _name = 'poultry.sale.report.line'
    _description = 'Poultry Sale Report Line'

    wizard_id = fields.Many2one('poultry.sale.report.wizard', ondelete='cascade')
    date = fields.Date(string="Date")
    branch_id = fields.Many2one('poultry.branch', string="Branch")
    poultry_type_id = fields.Many2one('poultry.type', string="Poultry Type")
    quantity = fields.Float(string="Quantity")
    unit_price = fields.Monetary(string="Unit Price", currency_field='currency_id')
    revenue = fields.Monetary(string="Revenue", currency_field='currency_id')
    buyer = fields.Char(string="Buyer")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
