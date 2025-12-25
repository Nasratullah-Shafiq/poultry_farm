# poultry_farm_management/models/farm.py
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

from odoo import models, fields, api


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
    item_type_id = fields.Many2one('item.type', string="Type")

    farm_id = fields.Many2one('poultry.farm', string='Farm')

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

    @api.model
    def create(self, vals):
        if not vals.get('code') and vals.get('name'):
            # Take first 3 letters of name
            prefix = vals['name'].replace(' ', '').upper()[:3]

            # Search last sequence with same prefix
            last_record = self.search(
                [('code', 'like', f'{prefix}-%')],
                order='code desc',
                limit=1
            )

            if last_record and last_record.code:
                last_number = int(last_record.code.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            vals['code'] = f"{prefix}-{str(new_number).zfill(3)}"

        return super(PoultryFarmHouse, self).create(vals)



    @api.depends('branch_id', 'item_type_id')
    def _compute_total_quantity(self):
        for house in self:
            if not house.branch_id or not house.item_type_id:
                house.current_stock = 0
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
            house.current_stock = max(total_purchased - total_deaths - total_sold, 0)
            house.last_updated = fields.Datetime.now()


