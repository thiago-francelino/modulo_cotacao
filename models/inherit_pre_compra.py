from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InheritPreCompra(models.Model):
    _inherit = 'product.product'

    product_cotacao = fields.Many2many(
        comodel_name="cotacao.wizard",
    )
    marca = fields.Char(related="fipe_ids.marca")
    ano = fields.Integer(related="fipe_ids.ano")
    codigo_fipe = fields.Char(related="fipe_ids.codigo_fipe")


    cotacoes_do_produto = fields.Integer(string="Cotado pelo cliente", default=0)

    valor_concorrente= fields.Float()

    # concorrente_ids = fields.One2many('concorrente', 'product_id', string="Concorrente")

    pode_comprar = fields.Boolean(
        string="Pode comprar",
        default=True
    )

    vai_comprar = fields.Boolean(
        string="Vai comprar",
        default=True
    )

    etq_insuficiente = fields.Boolean(
        string="Estoque insuficiente",
        help="Não atende ou atende "
             "parcialmente a demanda"
    )

    quantidade_requisitada = fields.Float(
        string="Quantidade requisitada",
    )

    valor_concorrente = fields.Float(string='Valor do concorrente')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        vetor = name.split(' ')

        records = []
        for rec in vetor:
            records.append('|')
            records.append('|')
            records.append('|')
            records.append('|')
            records.append('|')
            records.append(('name', operator, rec))
            records.append(('product_template_attribute_value_ids', operator, rec))
            records.append(('fipe_ids.name', operator, rec))
            records.append(('fipe_ids.marca', operator, rec))
            records.append(('fipe_ids.ano', operator, rec))
            records.append(('fipe_ids.codigo_fipe', operator, rec))
        if name:
            res = self.search(records)
            return res.name_get()
        return self.search([('name', operator, name)] + args, limit=limit).name_get()

    # product_cotacao_compute = fields.Integer(
    #     compute="onchange_product_quotes"
    # )

    # def onchange_product_quotes(self):
    #     quotes = self.env['cotacao.wizard'].search([])
    #     product_quotes = []
    #
    #     for quote in quotes:
    #         for product_line in quote.modulo_carrinho:
    #             if product_line.product_id.id.__eq__(self.id):
    #                 product_quotes.append(quote.id)
    #
    #     self.product_cotacao = product_quotes
    #     self.product_cotacao_compute = 1

    # def write(self, vals):
    #     if 'quantidade_requisitada' in vals:
    #         if vals['quantidade_requisitada'] > self.qty_available:
    #             raise UserError('O produto ' + self.name + ' tem estoque inferior a a quantidade requisitada.')
    #
    #     return super(InheritPreCompra, self).write(vals=vals)

    alt_flt_estoque = fields.Boolean(
        string="Alt flt desejado",
        help="É uma alternativa a falta de estoque "
             "ou cliente apresentou interesse alem "
             "do produto no qual ligou sobre"
    )

    alt_flt_variante = fields.Boolean(
        string="Alt flt variante",
        help="É uma alternativa a falta de estoque "
             "ou cliente apresentou interesse alem "
             "do produto no qual ligou sobre"
    )

    valor_concorrente = fields.Float()

    concorrente_ids = fields.One2many('concorrente', 'product_id', string="Concorrente")
