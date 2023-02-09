from odoo import models, fields, api, _


class Concorrente(models.Model):
    _name = 'concorrente'

    # nome = fields.Char(
    #     string="Nome do concorrente"
    # )
    #colocar domain tb de active = false
    concorrente_id = fields.Many2one(
        'res.partner',
        string="Concorrente",
        domain="[('concorrente','=',True),('active','=',False)]",
        required=True
    )

    valor_produto = fields.Float(
        string="Valor do concorrente",
        required=True
    )

    product_id = fields.Many2one(
        'product.product',
        string="Produto",
        required=True
    )

    # def criar_res_partner(self):
    #
    #     vals_list = ({
    #         'name':self.,
    #         'property_account_receivable_id':25,
    #         'property_account_payble_id':98,
    #         'active':False,
    #         'concorrente':True,
    #     })

