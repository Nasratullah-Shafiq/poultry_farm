
from odoo import models, fields, api
from odoo.exceptions import UserError



class PoultryType(models.Model):
    _name = 'item.type'
    _description = 'Item Type'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter

    name = fields.Char(string="Type Name", required=True)
    description = fields.Text(string="Description")




class PoultryFarm(models.Model):
    _name = 'poultry.farm'
    _description = 'Poultry Stock Overview'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    branch_id = fields.Many2one('poultry.branch', string='Branch', required=True)
    item_type_id = fields.Many2one('item.type', string='Type', required=True)
    total_quantity = fields.Integer(string="Total Quantity", default=0, tracking=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True,
                             default=lambda self: self.env.ref('uom.product_uom_unit'))
    last_updated = fields.Datetime(string="Last Updated", default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        """Override create to update stock after record creation"""
        rec = super(PoultryFarm, self).create(vals)
        rec._update_stock()
        return rec

    # def _update_stock(self):
    #     """Updates the total_quantity for the branch and item type"""
    #     for record in self:
    #         # Example: suppose you have a poultry.purchase model to get stock
    #         purchases = self.env['poultry.purchase'].search([
    #             ('branch_id', '=', record.branch_id.id),
    #             ('item_type_id', '=', record.item_type_id.id)
    #         ])
    #         total_qty = sum(p.quantity for p in purchases)
    #
    #         if total_qty == 0:
    #             raise UserError("No stock found for this branch and item type!")
    #
    #         record.total_quantity = total_qty
    #         record.last_updated = fields.Datetime.now()

    def _update_stock(self):
        """Update total_quantity by adding purchases and subtracting deaths"""
        for record in self:
            # Total purchased quantity for this branch and item type
            purchases = self.env['poultry.purchase'].search([
                ('branch_id', '=', record.branch_id.id),
                ('item_type_id', '=', record.item_type_id.id)
            ])
            total_purchased = sum(p.quantity for p in purchases)

            # Total deaths for this branch and item type
            deaths = self.env['poultry.death'].search([
                ('branch_id', '=', record.branch_id.id),
                ('item_type_id', '=', record.item_type_id.id)
            ])
            total_deaths = sum(d.quantity for d in deaths)

            # Calculate net stock
            net_quantity = total_purchased - total_deaths
            if net_quantity < 0:
                net_quantity = 0  # prevent negative stock

            record.total_quantity = net_quantity
            record.last_updated = fields.Datetime.now()
