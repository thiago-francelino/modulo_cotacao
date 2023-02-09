from odoo import models, fields, api, _
from datetime import date


# class PagamentoDireto(models.TransientModel):
class CotacaoWizard(models.Model):
    _name = "cotacao.wizard"

    cliente = fields.Many2one(
        'res.partner',
        string="Cliente"
    )

    cotacoes_cliente = fields.One2many(
        related="cliente.cotacoes_id",
        string="Cotações anteriores"
    )

    rota_id = fields.Many2one(
        'routes',
        string="Rota do cliente",
        readonly=True
    )

    data_vencimento_cotacao = fields.Date(
        string="Data", default=date.today()
    )

    termo_pagamento = fields.Many2one(
        'account.payment.term'
    )
    metodo_pagamento = fields.Many2one(
        'account.payment.method'
    )

    codigo_do_produto_busca = fields.Integer(
        string="Codigo do Produto",
        default=None
    )

    produto_desejado_id = fields.Many2one(
        'product.product',
        string="Produto desejado",
    )

    nome_produto_desejado_related = fields.Char(
        related="produto_desejado_id.name",
        string="Nome",
    )

    quantidade_requisitada_related = fields.Float(
        string="Quantidade requisitada",
        related="produto_desejado_id.quantidade_requisitada",
        default=None,
        help="Este campo é do inherit do product product",
        readonly=False
    )

    produto_desejado_quantidade_related = fields.Float(
        related="produto_desejado_id.virtual_available",
        string="Quantidade do produto em estoque"
    )

    optional_product_id = fields.Many2many(related='produto_desejado_id.optional_product_ids')

    template_related = fields.Many2one(related='produto_desejado_id.product_tmpl_id')

    #_____-------=====Campos relacionados as variantes de produto=====-------_____
    # odoo oficial
    variantes_produto_desejado_ids = fields.Many2one(
        'product.product',
        string="Variantes do produto",
        domain="[('product_tmpl_id','=',template_related),('id','!=',produto_desejado_id),('virtual_available','>',0)]"

    )
    # odoo home
    # variantes_produto_desejado_ids = fields.Many2one(
    #     'product.product',
    #     string="Variantes do produto",
    #
    # )

    quantidade_variante_requisitada = fields.Float(
        related="variantes_produto_desejado_ids.quantidade_requisitada",
        string="Quantidade requisitada",
        readonly=False
    )
    # _____-------=====Campos relacionados aos produtos alternativos=====-------_____
    # odoo oficial
    produto_alternativo_id = fields.Many2one(
        'product.product',
        string="Produto alternativo",
        domain="[('product_tmpl_id','in',optional_product_id),('virtual_available','>',0)]"
    )
    #odoo home
    # produto_alternativo_id = fields.Many2one(
    #     'product.product',
    #     string="Produto alternativo",
    # )

    quantidade_alternativo_requisitada = fields.Float(
        related="produto_alternativo_id.quantidade_requisitada",
        string="Quantidade requisitada",
        readonly=False,
    )

    # _____-------=====Campos relacionados aos acessorios dos 3 tipos de produto=====-------_____

    acessorio_desejado = fields.Many2many(
        related='produto_desejado_id.accessory_product_ids',
        string="Acessorios do produto"
    )

    acessorio_variante = fields.Many2many(
        related='variantes_produto_desejado_ids.accessory_product_ids',
        string="Acessorios do produto"
    )

    acessorio_alternativo = fields.Many2many(
        related='produto_alternativo_id.accessory_product_ids',
        string="Acessorios do produto"
    )

    # _____-------=====Campos relacionados aos carrinhos, o carrinho q o vendedor pode editar é o carrinho_ids=====-------_____

    carrinho_ids = fields.Many2one(
        'product.product',
        relation='rel_carrinho_product_cotacao',
        string="Carrinho"
    )

    carrinho_geral_ids = fields.Many2many(
        'product.product',
        relation='rel_carrinho_geral_product_cotacao',
        string="Carrinho geral",
        help="Este carrinho agrupa todos os produtos, "
             "os que o cliente teve interesse e os que"
             " serão de fato comprados"
    )

    modulo_carrinho = fields.One2many(
        'carrinho',
        'cotacao_id',
        string="Modulo de carrinho"
    )

    valor_total_comprado = fields.Integer(
        string="Valor total",
        readonly=True
    )

    variante_check = fields.Boolean(defalt=False)
    alternativo_check = fields.Boolean(defalt=False)
    desejado_check = fields.Boolean(defalt=False)
    desejado_insuficiente = fields.Boolean()



    def cria_prepedido(self):
        vals_list = {
            'partner_id': self.cliente.id,
            'validity_date': self.data_vencimento_cotacao,
            'payment_term_id': self.termo_pagamento.id,
        }

        quote = self.env['sale.order'].create(vals_list)



        for produtos in self.modulo_carrinho:
            if produtos.pode_comprar and produtos.vai_comprar:
            # name = produtos.name + '(' + produtos.product_template_attribute_value_ids.name + ')'

                vals_lines = ({
                    'order_line': [(0, 0, {'product_id': produtos.product_id.id,
                                           'product_template_id': produtos.product_id.product_tmpl_id.id,
                                           'product_uom_qty': produtos.product_id.quantidade_requisitada})]
                })
                quote.write(vals_lines)
            produtos.product_id.pode_comprar = True
            produtos.product_id.vai_comprar = True
            produtos.product_id.etq_insuficiente = False
            produtos.product_id.quantidade_requisitada = 0
            produtos.product_id.cotacoes_do_produto = 0


        for produtos in self.modulo_carrinho:
            vals = {'todos_produtos': produtos}
            quote.write(vals)


        ctx = dict()
        return {
            'type': "ir.actions.act_window",
            'view_type': "form",
            'view_mode': "form",
            'res_id': quote.id,
            'res_model': "sale.order",
            'views': [[self.env.ref("sale.view_order_form").id, 'form']],
            'target': 'current',
            'context': ctx
        }

    def wizard_mostra_valor(self):

        ctx = dict()
        ctx.update({

            'default_cliente': self.cliente.id,
            'default_data_vencimento_cotacao': self.data_vencimento_cotacao,
            'default_produto_desejado_id': self.produto_desejado_id.id,
            'default_produto_alternativo_id': self.produto_alternativo_id.id,
            'default_variantes_produto_desejado_ids': self.variantes_produto_desejado_ids.id,
            'default_carrinho_ids': self.carrinho_ids.ids,
            'default_carrinho_geral_ids': self.carrinho_geral_ids.ids,
            'default_desejado_check': True,
            'default_desejado_insuficiente': self.desejado_insuficiente,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'nome',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mostra.valor.wizard',
            'views': [
                [
                    self.env.ref("cotacao.form_mostra_valor_wizard").id,
                    'form']
            ],
            'context': ctx,
            'target': 'new'
        }

    def wizard_mostra_valor_variante(self):
        ctx = dict()
        ctx.update({

            'default_cliente': self.cliente.id,
            'default_data_vencimento_cotacao': self.data_vencimento_cotacao,
            'default_produto_desejado_id': self.produto_desejado_id.id,
            'default_carrinho_ids': self.carrinho_ids.ids,
            'default_carrinho_geral_ids': self.carrinho_geral_ids.ids,
            'default_variantes_produto_desejado_ids': self.variantes_produto_desejado_ids.id,
            'default_quantidade_variante_requisitada': self.quantidade_variante_requisitada,
            'default_produto_alternativo_id': self.produto_alternativo_id.id,
            'default_quantidade_alternativo_requisitada': self.quantidade_alternativo_requisitada,
            'default_variante_check': True,
            'default_alternativo_check': self.alternativo_check,
            'default_desejado_insuficiente': self.desejado_insuficiente,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'nome',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mostra.valor.wizard',
            'views': [
                [
                    self.env.ref("cotacao.form_mostra_valor_wizard").id,
                    'form']
            ],
            'context': ctx,
            'target': 'new'
        }

    def wizard_mostra_valor_variante_todas_opcoes(self):

        ctx = dict()
        ctx.update({

            'default_cliente': self.cliente.id,
            'default_data_vencimento_cotacao': self.data_vencimento_cotacao,
            'default_produto_desejado_id': self.produto_desejado_id.id,
            'default_carrinho_ids': self.carrinho_ids.ids,
            'default_carrinho_geral_ids': self.carrinho_geral_ids.ids,
            'default_variantes_produto_desejado_ids': self.variantes_produto_desejado_ids.id,
            'default_quantidade_variante_requisitada': self.quantidade_variante_requisitada,
            'default_quantidade_alternativo_requisitada': self.quantidade_alternativo_requisitada,
            'default_produto_alternativo_id': self.produto_alternativo_id.id,
            'default_variante_check': self.variante_check,
            'default_alternativo_check': self.alternativo_check,
            'default_desejado_insuficiente': self.desejado_insuficiente,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'nome',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mostra.valor.wizard',
            'views': [
                [
                    self.env.ref("cotacao.form_mostra_valor_wizard").id,
                    'form']
            ],
            'context': ctx,
            'target': 'new'
        }

    @api.onchange('cliente')
    def preenche_rota(self):
        if self.cliente:
            self.rota_id = self.cliente.route_id

    @api.onchange('modulo_carrinho')
    def total_comprado(self):
        for rec in self.modulo_carrinho:
            if rec.vai_comprar and rec.pode_comprar:
                self.valor_total_comprado += rec.product_id.lst_price


    @api.onchange('data_vencimento_cotacao')
    def trata_data(self):
        if self.data_vencimento_cotacao:
            if self.data_vencimento_cotacao < date.today():
                self.data_vencimento_cotacao = date.today()

    @api.onchange('codigo_do_produto_busca')
    def busca_produto_por_id(self):
        if self.codigo_do_produto_busca:
            self.produto_desejado_id = self.codigo_do_produto_busca

    @api.onchange('produto_desejado_id')
    def calcula_cotacoes_anteriores_desejado(self):
        self.produto_desejado_id.cotacoes_do_produto = 0
        for cotacao in self.cotacoes_cliente:
            for carrinho in cotacao.modulo_carrinho:
                if carrinho.product_id.id == self.produto_desejado_id.id:
                    self.produto_desejado_id.cotacoes_do_produto += 1

    @api.onchange('variantes_produto_desejado_ids')
    def calcula_cotacoes_anteriores_variante(self):
        self.variantes_produto_desejado_ids.cotacoes_do_produto = 0
        for cotacao in self.cotacoes_cliente:
            for carrinho in cotacao.modulo_carrinho:
                if carrinho.product_id.id == self.variantes_produto_desejado_ids.id:
                    self.variantes_produto_desejado_ids.cotacoes_do_produto += 1

    @api.onchange('produto_alternativo_id')
    def calcula_cotacoes_anteriores_alternativo(self):
        self.produto_alternativo_id.cotacoes_do_produto = 0
        for cotacao in self.cotacoes_cliente:
            for carrinho in cotacao.modulo_carrinho:
                if carrinho.product_id.id == self.produto_alternativo_id.id:
                    self.produto_alternativo_id.cotacoes_do_produto += 1
