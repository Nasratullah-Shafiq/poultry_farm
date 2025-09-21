# poultry_farm_management/__manifest__.py
{
    'name': 'Poultry Farm Management',
    'version': '17.0.1.0.0',
    'category': 'Agriculture',
    'sequence': -200,
    'summary': 'Manage poultry purchases, sales, feed, medicine, HR and finance for multi-branch farms',
    'description': """
Poultry Farm Management system:
- Multi-branch (one main + two sub-branches)
- Human Resources (employees, attendance placeholder, salaries)
- Finance (income/expenses, branch reports)
- Farm (poultry purchase/sales, feed & medicine inventory, vaccination schedules)
""",
    'author': 'Nasratullah Shafiq / Generated',
    'depends': ['base', 'hr', 'account'],
    'data': [
    'security/ir.model.access.csv',

    # Menus should load first
    'views/menu.xml',

    # Wizard and view files
    'views/finance_report_wizard_views.xml',
    'views/branch_views.xml',
    'views/employee_views.xml',
    'views/finance_views.xml',
    'views/farm_views.xml',

    # Reports - actions before templates
    'report/finance_report_action.xml',
    'report/finance_report_template.xml',
],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
