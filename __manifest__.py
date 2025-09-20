# poultry_farm_management/__manifest__.py
{
    'name': 'Poultry Farm Management',
    'version': '17.0.1.0.0',
    'category': 'Agriculture',
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
        'views/menu.xml',
        'views/branch_views.xml',
        'views/employee_views.xml',
        'views/finance_views.xml',
        'views/farm_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
