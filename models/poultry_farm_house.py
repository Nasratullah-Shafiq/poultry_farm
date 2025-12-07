# poultry_farm_management/models/farm.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class PoultryFarmHouse(models.Model):
    _name = 'poultry.farm.house'
    _description = 'Poultry Farm House'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Farm Name', required=True, tracking=True)
    code = fields.Char(string='Farm Code', tracking=True, readonly=True)

    branch_id = fields.Many2one('poultry.branch', string='Branch', required=True, tracking=True, ondelete='cascade')
    location = fields.Char(string='Location / Address')
    capacity = fields.Integer(string='Capacity (birds)')
    # current_stock = fields.Integer(string='Current Stock (birds)' ,computed="_compute_available_quantity", readonly=True)
    # current_stock = fields.Integer(
    #     string='Current Stock (birds)',
    #     # related='sale_id.total_quantity',
    #     store=True,
    #     readonly=True
    # )
    # current_stock = fields.Integer(related="sale_id.available_quantity", store=True)

    farm_id = fields.Many2one('poultry.farm', string='Farm', required=True)

    # current_stock = fields.Integer(
    #     string='Current Stock (birds)',
    #     related='farm_id.total_quantity',
    #     store=True,
    #     readonly=True
    # )

    manager_id = fields.Many2one('res.partner', string='Manager')

    state = fields.Selection([
        ('operational', 'Operational'),
        ('maintenance', 'Maintenance'),
        ('closed', 'Closed'),
    ], default='operational', tracking=True)
    active = fields.Boolean(default=True)
    note = fields.Text()

    current_stock = fields.Integer(
        string="Total Chickens",
        compute="_compute_total_chickens",
        store=True
    )

    @api.depends('farm_stock_ids.total_quantity')  # depends on the One2many stock records
    def _compute_current_stock(self):
        for rec in self:
            total_chickens = 0
            # Iterate only stock records for this house
            for stock in rec.farm_stock_ids:
                # Filter by chicken item type if needed
                if stock.item_type_id.name.lower() == "chicken":
                    total_chickens += stock.total_quantity
            rec.current_stock = total_chickens

    # Auto-generate farm code using sequence
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('poultry.farm.seq') or '/'
        return super().create(vals)

    # @api.depends('branch_id', 'farm_id', 'item_type_id')
    # def _compute_available_quantity(self):
    #     """Compute available stock based on branch + farm + item type."""
    #     for rec in self:
    #         if rec.branch_id and rec.farm_id and rec.item_type_id:
    #
    #             stock = self.env['poultry.farm'].search([
    #                 ('branch_id', '=', rec.branch_id.id),
    #                 ('farm_id', '=', rec.farm_id.id),
    #                 ('item_type_id', '=', rec.item_type_id.id)
    #             ], limit=1)
    #
    #             rec.available_quantity = stock.current_stock if stock else 0
    #
    #         else:
    #             rec.available_quantity = 0
