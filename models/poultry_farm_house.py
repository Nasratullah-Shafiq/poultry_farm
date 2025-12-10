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
    # Add item type
    item_type_id = fields.Many2one('item.type', string="Type", required=True)

    farm_id = fields.Many2one('poultry.farm', string='Farm', required=True)

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
        compute="_compute_total_quantity",
        store=True
    )

    class PoultryFarmHouse(models.Model):
        _name = 'poultry.farm.house'
        _description = 'Farm House'

        name = fields.Char(string="Farm House Name", required=True)
        branch_id = fields.Many2one('poultry.branch', string="Branch", required=True)
        item_type_id = fields.Many2one('item.type', string="Poultry Type", required=True)

        total_quantity = fields.Integer(
            string="Total Quantity",
            compute="_compute_total_quantity",
            store=True
        )
        last_updated = fields.Datetime(string="Last Updated", default=fields.Datetime.now)

        @api.depends('branch_id', 'item_type_id')
        def _compute_total_quantity(self):
            for house in self:
                if not house.branch_id or not house.item_type_id:
                    house.total_quantity = 0
                    continue

                # Total purchased quantity for this farm house
                purchases = self.env['poultry.purchase'].search([
                    ('branch_id', '=', house.branch_id.id),
                    ('item_type_id', '=', house.item_type_id.id),
                    ('farm_id', '=', house.id),
                ])
                total_purchased = sum(p.quantity for p in purchases)

                # Total deaths for this farm house
                deaths = self.env['poultry.death'].search([
                    ('branch_id', '=', house.branch_id.id),
                    ('item_type_id', '=', house.item_type_id.id),
                    ('farm_id', '=', house.id),
                ])
                total_deaths = sum(d.quantity for d in deaths)

                # Total sold quantity for this farm house (if you track sales)
                sales = self.env['poultry.sale'].search([
                    ('branch_id', '=', house.branch_id.id),
                    ('item_type_id', '=', house.item_type_id.id),
                    ('farm_id', '=', house.id),
                ])
                total_sold = sum(s.quantity for s in sales)

                # Net stock
                house.total_quantity = max(total_purchased - total_deaths - total_sold, 0)
                house.last_updated = fields.Datetime.now()
