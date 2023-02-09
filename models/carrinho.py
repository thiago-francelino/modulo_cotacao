from odoo import models, fields, api, _


class InheritProduct(models.Model):
    _name = 'carrinho'

    product_id = fields.Many2one('product.product')

    valor_produto = fields.Float(related="product_id.lst_price")

    cotacao_id = fields.Many2one('cotacao.wizard')
    imagem = fields.Binary(related="product_id.image_1920")
    nome = fields.Char(related="product_id.fipe_ids.name")
    marca = fields.Char(related="product_id.fipe_ids.marca")
    ano = fields.Integer(related="product_id.fipe_ids.ano")
    codigo_fipe = fields.Char(related="product_id.fipe_ids.codigo_fipe")

    pode_comprar = fields.Boolean(
        string="Pode comprar",
        default=True
    )

    vai_comprar = fields.Boolean(
        string="Vai comprar",
        default=True
    )


    etq_insuficiente = fields.Boolean(
        string="Estoque insufuciente?",
        help="Não atende ou atende "
             "parcialmente a demanda",
        default=False
    )

    quantidade_requisitada = fields.Integer(
        string="Quantidade requisitada",
        default=None
    )
