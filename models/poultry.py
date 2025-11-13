
from odoo import models, fields, api
from datetime import date, timedelta


class PoultryType(models.Model):
    _name = 'item.type'
    _description = 'Item Type'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter

    name = fields.Char(string="Type Name", required=True)
    description = fields.Text(string="Description")


# class Poultry(models.Model):
#     _name = 'poultry.farm'
#     _description = 'Poultry Record'
#     _rec_name = 'name'
#     _inherit = ['mail.thread', 'mail.activity.mixin']  # <-- Add chatter support
#
#     name = fields.Char(string="Name", required=True)
#     age = fields.Integer(string="Age (Weeks)", required=True)
#
#     gender = fields.Selection(
#         [
#             ('male', 'Male'),
#             ('female', 'Female')
#         ],
#         string="Gender",
#         required=True
#     )
#
#     poultry_type_id = fields.Many2one(
#         'poultry.type',
#         string='Poultry Type',
#         required=True,
#         help="Select the type of poultry, e.g., Broiler, Layer, Duck, etc."
#     )
#
#     branch_id = fields.Many2one(
#         'poultry.branch',
#         string='Branch',
#         help="The branch where this poultry is located"
#     )
#     quantity = fields.Integer(
#         string="Quantity",
#         required=True,
#         default=0,
#         help="Number of birds in this poultry record"
#     )
#
#     description = fields.Text(string="Description")
#     date_added = fields.Date(string="Date Added", default=fields.Date.today)
#
#     # Computed field for search panel
#     date_category = fields.Selection(
#         [
#             ('today', 'Today'),
#             ('week', 'This Week'),
#             ('month', 'This Month'),
#             ('older', 'Older'),
#         ],
#         string="Date Category",
#         compute="_compute_date_category",
#         store=True
#     )
#     # One2many for Sales
#     sale_ids = fields.One2many(
#         'poultry.sale',  # Child model name
#         'poultry_id',  # Field in the child model
#         string='Sales'
#     )
#
#     # One2many to Death Records
#     death_ids = fields.One2many(
#         'poultry.death',
#         'poultry_id',
#         string="Death Records"
#     )
#
#     # Computed field for remaining birds (after sales & deaths)
#     remaining_quantity = fields.Integer(
#         string="Remaining Quantity",
#         compute="_compute_remaining_quantity",
#         store=True
#     )
#
#     # Computed field for live birds (total quantity - deaths)
#     live_quantity = fields.Integer(
#         string="Live Birds",
#         compute="_compute_live_quantity",
#         store=True
#     )
#
#     @api.depends('quantity', 'sale_ids.quantity', 'death_ids.quantity')
#     def _compute_remaining_quantity(self):
#         """Calculate remaining quantity after sales and deaths"""
#         for record in self:
#             total_sold = sum(record.sale_ids.mapped('quantity'))
#             total_deaths = sum(record.death_ids.mapped('quantity'))
#             record.remaining_quantity = record.quantity - total_sold - total_deaths
#
#     @api.depends('quantity', 'death_ids.quantity')
#     def _compute_live_quantity(self):
#         """Calculate live birds excluding deaths only"""
#         for record in self:
#             total_deaths = sum(record.death_ids.mapped('quantity'))
#             record.live_quantity = record.quantity - total_deaths
#
#     @api.depends('quantity', 'sale_ids.quantity')
#     def _compute_remaining_quantity(self):
#         for record in self:
#             total_sold = sum(record.sale_ids.mapped('quantity'))
#             record.remaining_quantity = record.quantity - total_sold
#
#
#     @api.depends('date_added')
#     def _compute_date_category(self):
#         today = date.today()
#         week_start = today - timedelta(days=today.weekday())
#         month_start = today.replace(day=1)
#         for record in self:
#             if not record.date_added:
#                 record.date_category = False
#             elif record.date_added == today:
#                 record.date_category = 'today'
#             elif record.date_added >= week_start:
#                 record.date_category = 'week'
#             elif record.date_added >= month_start:
#                 record.date_category = 'month'
#             else:
#                 record.date_category = 'older'

# class Poultry(models.Model):
#     _name = 'poultry.farm'
#     _description = 'Poultry Record'
#     _rec_name = 'name'
#     _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter
#
#     # name = fields.Char(string="Name", required=True)
#     name = fields.Char(
#         string="Name",
#         required=True,
#         default="Broiler",
#         readonly=True
#     )
#     age = fields.Integer(string="Age (Weeks)", required=True)
#
#     # gender = fields.Selection(
#     #     [
#     #         ('male', 'Male'),
#     #         ('female', 'Female')
#     #     ],
#     #     string="Gender",
#     #     required=True
#     # )
#
#     # poultry_type_id = fields.Many2one(
#     #     'poultry.type',
#     #     string='Poultry Type',
#     #     required=True,
#     #     help="Select the type of poultry, e.g., Broiler, Layer, Duck, etc."
#     # )
#
#     branch_id = fields.Many2one(
#         'poultry.branch',
#         string='Branch',
#         help="The branch where this poultry is located",
#         required=True,
#     )
#
#     quantity = fields.Integer(
#         string="Initial Quantity",
#         required=True,
#         default=0,
#         help="Total birds added initially in this batch."
#     )
#
#     description = fields.Text(string="Description")
#     date_added = fields.Date(string="Date Added", default=fields.Date.today)
#
#     # Computed field for search panel
#     date_category = fields.Selection(
#         [
#             ('today', 'Today'),
#             ('week', 'This Week'),
#             ('month', 'This Month'),
#             ('older', 'Older'),
#         ],
#         string="Date Category",
#         compute="_compute_date_category",
#         store=True
#     )
#
#     # One2many for Sales
#     # sale_ids = fields.One2many(
#     #     'poultry.sale',  # Child model name
#     #     'poultry_id',    # Field in the child model
#     #     string='Sales'
#     # )
#
#     # One2many to Death Records
#     # death_ids = fields.One2many(
#     #     'poultry.death',
#     #     'poultry_id',
#     #     string="Death Records"
#     # )
#
#     # Computed field for remaining birds (after sales & deaths)
#     remaining_quantity = fields.Integer(
#         string="Remaining Quantity",
#         # compute="_compute_remaining_quantity",
#         store=True
#     )
#
#     # Computed field for live birds (total quantity - deaths)
#     live_quantity = fields.Integer(
#         string="Live Birds",
#         compute="_compute_live_quantity",
#         store=True
#     )
#
#     total_quantity = fields.Integer(string="Total Quantity", compute="_compute_total_quantity")
#
#     @api.depends('quantity')
#     def _compute_total_quantity(self):
#         total = sum(self.mapped('quantity'))
#         for rec in self:
#             rec.total_quantity = total
#
#     @api.model
#     def action_save_record(self):
#         """Custom logic when the Save button is clicked"""
#         # Example: just log a message or do extra validation
#         for record in self:
#             record.message_post(body="Custom save button clicked!")
#         return True
#
#     def action_discard_record(self):
#         """Close the form without saving"""
#         return {'type': 'ir.actions.act_window_close'}
#
#     # @api.depends('quantity', 'sale_ids.quantity', 'death_ids.quantity')
#     # def _compute_remaining_quantity(self):
#     #     """Calculate remaining quantity after sales and deaths"""
#     #     for record in self:
#     #         total_sold = sum(record.sale_ids.mapped('quantity'))
#     #         total_deaths = sum(record.death_ids.mapped('quantity'))
#     #         record.remaining_quantity = record.quantity - total_sold - total_deaths
#     # @api.depends('quantity', 'sale_ids.quantity', 'death_ids.quantity', 'branch_id')
#     # def _compute_remaining_quantity(self):
#     #     """Calculate remaining quantity based on selected branch"""
#     #     for record in self:
#     #         if not record.branch_id:
#     #             # If no branch selected, just show total quantity minus total sales/deaths
#     #             total_sold = sum(record.sale_ids.mapped('quantity'))
#     #             total_deaths = sum(record.death_ids.mapped('quantity'))
#     #             record.remaining_quantity = record.quantity - total_sold - total_deaths
#     #         else:
#     #             # Filter sales and deaths by branch
#     #             total_sold = sum(record.sale_ids.filtered(lambda s: s.branch_id == record.branch_id).mapped('quantity'))
#     #             total_deaths = sum(
#     #                 record.death_ids.filtered(lambda d: d.branch_id == record.branch_id).mapped('quantity'))
#     #             record.remaining_quantity = record.quantity - total_sold - total_deaths
#
#     # @api.depends('quantity', 'death_ids.quantity')
#     # def _compute_live_quantity(self):
#     #     """Calculate live birds excluding deaths only"""
#     #     for record in self:
#     #         total_deaths = sum(record.death_ids.mapped('quantity'))
#     #         record.live_quantity = record.quantity - total_deaths
#
#     @api.depends('date_added')
#     def _compute_date_category(self):
#         """Categorize by date for filtering/search"""
#         today = date.today()
#         week_start = today - timedelta(days=today.weekday())
#         month_start = today.replace(day=1)
#         for record in self:
#             if not record.date_added:
#                 record.date_category = False
#             elif record.date_added == today:
#                 record.date_category = 'today'
#             elif record.date_added >= week_start:
#                 record.date_category = 'week'
#             elif record.date_added >= month_start:
#                 record.date_category = 'month'
#             else:
#                 record.date_category = 'older'

class PoultryFarm(models.Model):
    _name = 'poultry.farm'
    _description = 'Poultry Stock Overview'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    branch_id = fields.Many2one('poultry.branch', string='Branch', required=True)
    item_type_id = fields.Many2one('item.type', string='Type', required=True)
    total_quantity = fields.Integer(string="Total Quantity", default=0, tracking=True)
    last_updated = fields.Datetime(string="Last Updated", default=fields.Datetime.now)

