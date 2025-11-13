from odoo import models, fields, api



class PoultryDeath(models.Model):
    _name = 'poultry.death'
    _description = 'Poultry Death Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'date'

    # poultry_id = fields.Many2one(
    #     'poultry.farm',
    #     string="Poultry Batch",
    #     required=True,
    #     ondelete='cascade'
    # )
    branch_id = fields.Many2one(
        'poultry.branch',
        string="Branch",
        # readonly=True,
        store=True,
        help="Branch is automatically fetched from the Poultry Batch"
    )

    date = fields.Date(
        string="Date of Death",
        required=True,
        default=fields.Date.today
    )

    quantity = fields.Integer(
        string="Number of Dead Birds",
        required=True
    )

    reason = fields.Selection(
        [
            ('disease', 'Disease'),
            ('injury', 'Injury'),
            ('natural', 'Natural Cause'),
            ('unknown', 'Unknown')
        ],
        string="Reason",
        required=True
    )

    description = fields.Text(string="Additional Notes")
    notes = fields.Text(string="Additional Notes")


    death_count = fields.Integer(
        string="Total Deaths in Batch",
        compute="_compute_death_count",
        store=True
    )
    
    

    # # ✅ Related field to show remaining quantity from poultry farm
    # remaining_quantity = fields.Integer(
    #     string="Remaining Quantity",
    #     related="poultry_id.remaining_quantity",
    #     store=False,
    #     readonly=True
    # )
    #
    # @api.depends('poultry_id.death_ids.quantity')
    # def _compute_death_count(self):
    #     """Compute total deaths for this poultry batch"""
    #     for record in self:
    #         if record.branch_id:
    #             record.death_count = sum(record.branch_id.death_ids.mapped('quantity'))
    #         else:
    #             record.death_count = 0

    # ✅ Computed remaining quantity based on poultry type AND branch
    remaining_quantity = fields.Integer(
        string="Remaining Quantity",
        # compute='_compute_remaining_quantity',
        store=False,
        readonly=True
    )

    # @api.depends('branch_id')
    # def _compute_remaining_quantity(self):
    #     for record in self:
    #         if record.poultry_id and record.branch_id:
    #             # Get all deaths for this poultry and branch
    #             total_deaths = self.env['poultry.death'].search([
    #                 ('poultry_id', '=', record.poultry_id.id),
    #                 ('branch_id', '=', record.branch_id.id)
    #             ])
    #             dead_qty = sum(total_deaths.mapped('quantity'))
    #
    #             # Calculate remaining quantity for this poultry in this branch
    #             record.remaining_quantity = max(record.poultry_id.quantity - dead_qty, 0)
    #         else:
    #             record.remaining_quantity = 0