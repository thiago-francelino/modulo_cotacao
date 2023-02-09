from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class MostraValorWizard(models.TransientModel):
    _name = "mostra.valor.wizard"

    cliente = fields.Many2one(
        'res.partner',
        string="Cliente"
    )

    data_vencimento_cotacao = fields.Date(
        string="Data",
    )


    produto_desejado_id = fields.Many2one(
        'product.product',
        string="Produto desejado"
    )

    concorrente_id = fields.Many2one(
        'res.partner',
        string="Concorrente",
        domain="[('concorrente','=',True),('active','=',False)]",
        required=True
    )
    concorrente_desejado = fields.One2many(related='produto_desejado_id.concorrente_ids')

    valor_concorrente_desejado = fields.Float(
        related="produto_desejado_id.valor_concorrente",
        readonly=False
    )

    quantidade_requisitada_related = fields.Float(
        string="Quantidade requisitada",
        related="produto_desejado_id.quantidade_requisitada",
        default=None,
        help="Este campo é do inherit do product product",
        readonly=False
    )

    produto_desejado_related_valor_id = fields.Float(
        related='produto_desejado_id.lst_price',
        string="Valor"
    )

    produto_desejado_quantidade_desejada_id = fields.Float(
        related='produto_desejado_id.quantidade_requisitada',
        string="Quantidade requisitada",
        readonly=False,
        store=True,
    )


    quantidade_requisitada = fields.Float(
        string="Quantidade requisitada",
        default=None
    )

    produto_desejado_quantidade_related = fields.Float(
        related="produto_desejado_id.virtual_available",
        string="Estoque"
    )

    # _____-------=====Campos relacionados as variantes de produto=====-------_____

    variantes_produto_desejado_ids = fields.Many2one(
        'product.product',
        string="Variantes do produto",

    )

    valor_concorrente_variante = fields.Float(
        related="variantes_produto_desejado_ids.valor_concorrente",
        readonly=False
    )


    quantidade_variante_requisitada = fields.Float(
        related="variantes_produto_desejado_ids.quantidade_requisitada",
        string="Quantidade requisitada",
        readonly=False
    )
    estoque_variante = fields.Float(
        related="variantes_produto_desejado_ids.virtual_available",
        string="Estoque variante"
    )
    valor_variante = fields.Float(
        related="variantes_produto_desejado_ids.lst_price",
        string="Valor variante"
    )

    # _____-------=====Campos relacionados ao produto alternativo=====-------_____

    produto_alternativo_id = fields.Many2one(
        'product.product',
        string="Produto alternativo",
    )

    valor_concorrente_alternativo = fields.Float(
        related="produto_alternativo_id.valor_concorrente",
        readonly=False
    )

    produto_alternativo_related_valor_id = fields.Float(
        related='produto_alternativo_id.lst_price',
        string="Valor"
    )


    quantidade_alternativo_requisitada = fields.Float(
        related="produto_alternativo_id.quantidade_requisitada",
        string="Quantidade requisitada",
        readonly=False
    )

    estoque_alternativo = fields.Float(
        related="produto_alternativo_id.virtual_available",
        string="Estoque alternativo"
    )
    valor_alternativo = fields.Float(
        related="produto_alternativo_id.lst_price",
        string="Valor do alternativo"
    )

    acessorio_desejado = fields.Many2many(
        'product.product',
        relation="rel_acessorio_desejado_product",
        string="Acessorios do produto",
        domain="[('virtual_available','>',0)]"
    )

    acessorio_variante = fields.Many2many(
        'product.product',
        relation="rel_acessorio_variante_product",
        string="Acessorios do produto",
        domain="[('virtual_available','>',0)]"
    )

    acessorio_alternativo = fields.Many2many(
        'product.product',
        relation="rel_acessorio_alternativo_product",
        string="Acessorios do produto",
        domain="[('virtual_available','>',0)]"
    )

    carrinho_ids = fields.Many2many(
        'product.product',
        relation='rel_carrinho_product_mostra_valor',
        string="Carrinho"
    )

    carrinho_geral_ids = fields.Many2many(
        'product.product',
        relation='rel_carrinho_geral_product_mostra_valor',
        string="Carrinho geral",
        help="Este carrinho agrupa todos os produtos, os que"
             " o cliente teve interesse e os que serão de "
             "fato comprados"
    )

    # concorrente = fields.One2many('concorrente', string="Concorrente")

    # _____-------=====Booleans que são usados como controle são passados da primeira pra segunda tela=====-------_____

    desejado_check = fields.Boolean()
    variante_check = fields.Boolean()
    alternativo_check = fields.Boolean()
    desejado_insuficiente = fields.Boolean()

    #estas 3 variaveis fazem a mesma coisa são usadas para sumir com um group que
    # possui um aviso ao usuario tive que usar tres pois por algum motivo quando
    # eu usava a mesma os campos que eu queria não sumiam

    some_enviar = fields.Boolean()
    some_enviar_variante = fields.Boolean()
    some_enviar_alternativo = fields.Boolean()

    # _____-------=====Funções de validação dos campos de acessorio=====-------_____

    @api.onchange('acessorio_desejado')
    def valida_acessorio_desejado(self):
        if self.acessorio_desejado.quantidade_requisitada > self.acessorio_desejado.virtual_available:
            raise UserError('Algum dos produtos no campo de acessorios esta com quantidade requisitada maior que o estoque do mesmo')
        if self.acessorio_desejado.quantidade_requisitada == 0:
            self.acessorio_desejado.pode_comprar = False
        elif self.acessorio_desejado.quantidade_requisitada != 0:
            self.acessorio_desejado.pode_comprar = True

    @api.onchange('acessorio_variante')
    def valida_acessorio_variante(self):
        if self.acessorio_variante.quantidade_requisitada > self.acessorio_variante.virtual_available:
            raise UserError(
                'Algum dos produtos no campo de acessorios esta com quantidade requisitada maior que o estoque do mesmo')
        if self.acessorio_variante.quantidade_requisitada == 0:
            self.acessorio_variante.pode_comprar = False
        elif self.acessorio_variante.quantidade_requisitada != 0:
            self.acessorio_variante.pode_comprar = True

    @api.onchange('acessorio_alternativo')
    def valida_acessorio_alternativo(self):
        if self.acessorio_alternativo.quantidade_requisitada > self.acessorio_alternativo.virtual_available:
            raise UserError(
                'Algum dos produtos no campo de acessorios esta com quantidade requisitada maior que o estoque do mesmo')
        if self.acessorio_alternativo.quantidade_requisitada == 0:
            self.acessorio_alternativo.pode_comprar = False
        elif self.acessorio_alternativo.quantidade_requisitada != 0:
            self.acessorio_alternativo.pode_comprar = True

    # _____-------=====funçoes de validação da quantidade requirida pelo cliente=====-------_____
    #o requisito de marcar ou desmarcar estoque insufuciente é somente para o produto desejado
    @api.onchange('quantidade_requisitada_related')
    def valor_adequado_desejado(self):
        if self.quantidade_requisitada_related == 0:
            self.produto_desejado_id.pode_comprar = False
        else:
            self.produto_desejado_id.pode_comprar = True
        if self.produto_desejado_id:
            for rec in self.produto_desejado_id.accessory_product_ids:
                self.acessorio_desejado = [(6, 0, [rec.id])]
        if self.quantidade_requisitada_related > self.produto_desejado_id.virtual_available:
            self.produto_desejado_id.etq_insuficiente = True
            self.desejado_insuficiente = True
            self.some_enviar = True

        elif self.quantidade_requisitada_related <= self.produto_desejado_id.virtual_available:
            self.some_enviar = False

    @api.onchange('quantidade_variante_requisitada')
    def valor_adequado_variante(self):
        if self.quantidade_variante_requisitada == 0:
            self.variantes_produto_desejado_ids.pode_comprar = False
        else:
            self.variantes_produto_desejado_ids.pode_comprar = True
        if self.variantes_produto_desejado_ids:
            for rec in self.variantes_produto_desejado_ids.accessory_product_ids:
                self.acessorio_variante = [(6, 0, [rec.id])]

        if self.quantidade_variante_requisitada > self.variantes_produto_desejado_ids.virtual_available:
            if self.desejado_insuficiente:
                self.variantes_produto_desejado_ids.alt_flt_estoque = True
            # self.variantes_produto_desejado_ids.etq_insuficiente = True
            self.some_enviar_variante = True

        elif self.quantidade_variante_requisitada <= self.variantes_produto_desejado_ids.virtual_available:
            if self.desejado_insuficiente:
                self.variantes_produto_desejado_ids.alt_flt_estoque = True
            self.some_enviar_variante = False

    @api.onchange('quantidade_alternativo_requisitada')
    def valor_adequado_alternativo(self):
        if self.quantidade_alternativo_requisitada == 0:
            self.produto_alternativo_id.pode_comprar = False
        else:
            self.produto_alternativo_id.pode_comprar = True
        if self.produto_alternativo_id:
            for rec in self.produto_alternativo_id.accessory_product_ids:
                self.acessorio_alternativo = [(6, 0, [rec.id])]
        if self.quantidade_alternativo_requisitada > self.produto_alternativo_id.virtual_available:
            # self.produto_alternativo_id.etq_insuficiente = True
            self.some_enviar_alternativo = True

        elif self.quantidade_variante_requisitada <= self.variantes_produto_desejado_ids.virtual_available:
            self.some_enviar_alternativo = False

    # _____-------=====Essa função seleciona/cria automaticamente o produto caso seja necessario criar um concorrente=====-------_____

    # @api.onchange('produto_desejado_id')
    # def seleciona_produto(self):
    #     self.produto_desejado_id.concorrente_ids = [(0,0,{'product_id': self.produto_desejado_id.id})]

    # _____-------=====Essa função cria um objeto no carrinho=====-------_____

    def cria_objeto_carrinho(self, objeto):
        global cotacao_id
        cotacao_id = self.env.context.get("active_id")
        if objeto.pode_comprar == False:
            objeto.vai_comprar = False
        vals_list = {
            'product_id': objeto.id,
            'cotacao_id': self.env.context.get("active_id"),
            'pode_comprar': objeto.pode_comprar,
            'vai_comprar': objeto.vai_comprar,
            'etq_insuficiente': objeto.etq_insuficiente,
            'quantidade_requisitada': objeto.quantidade_requisitada,
        }
        self.env['carrinho'].create(vals_list)

    # _____-------=====As funções a seguir voltam pra primeira tela=====-------_____
    def wizard_volta_cotacao_variante(self):


        if self.acessorio_desejado:
            for rec in self.acessorio_desejado:
                if rec.quantidade_requisitada == 0:
                    rec.pode_comprar = False
                    rec.vai_comprar = False
                    self.cria_objeto_carrinho(rec)
                else:
                    rec.pode_comprar = True
                    self.cria_objeto_carrinho(rec)
        # if self.concorrente_desejado:
        #     for rec in self.concorrente_desejado:

        self.cria_objeto_carrinho(self.produto_desejado_id)
        vals_list_retorno = {
            'alternativo_check': False,
            'variante_check': True,
            'produto_alternativo_id': False,
            'variantes_produto_desejado_ids': False,
            'desejado_check': False,
        }

        record = self.env['cotacao.wizard'].browse(cotacao_id)
        record.write(vals_list_retorno)

        return


    def wizard_volta_cotacao_todas_opcoes(self):
        if self.concorrente_id and self.valor_concorrente_desejado:
            vals_list = {
                'concorrente_id': self.concorrente_id,
                'valor_produto': self.valor_concorrente_desejado,
                'product_id': self.produto_desejado_id,
            }
            self.env['concorrente'].create(vals_list)
        if self.acessorio_variante:
            for rec in self.acessorio_variante:
                if rec.quantidade_requisitada == 0:
                    rec.pode_comprar = False
                    rec.vai_comprar = False
                    self.cria_objeto_carrinho(rec)
                else:
                    rec.pode_comprar = True
                    self.cria_objeto_carrinho(rec)

        if self.variantes_produto_desejado_ids:
            if self.desejado_insuficiente:
                self.variantes_produto_desejado_ids.alt_flt_estoque = True
                self.cria_objeto_carrinho(self.variantes_produto_desejado_ids)
            else:
                self.variantes_produto_desejado_ids.alt_flt_estoque = False
                self.cria_objeto_carrinho(self.variantes_produto_desejado_ids)
        vals_list_retorno = {
            'alternativo_check': True,
            'variante_check': True,
            'produto_alternativo_id': False,
            'variantes_produto_desejado_ids': False,
            'desejado_check': False,
        }

        record = self.env['cotacao.wizard'].browse(cotacao_id)
        record.write(vals_list_retorno)

        return

    def wizard_volta_cotacao_final(self):
        if self.concorrente_id and self.valor_concorrente_desejado:
            vals_list = {
                'concorrente_id': self.concorrente_id,
                'valor_produto': self.valor_concorrente_desejado,
                'product_id': self.produto_desejado_id,
            }
            self.env['concorrente'].create(vals_list)

        if self.desejado_check:
            if self.produto_desejado_id:
                self.cria_objeto_carrinho(self.produto_desejado_id)

            if self.acessorio_desejado:
                for rec in self.acessorio_desejado:
                    if rec.quantidade_requisitada == 0:
                        rec.pode_comprar = False
                        rec.vai_comprar = False
                        self.cria_objeto_carrinho(rec)
                    else:
                        rec.pode_comprar = True
                        self.cria_objeto_carrinho(rec)
        self.desejado_check = False

        if self.acessorio_variante:
            for rec in self.acessorio_variante:
                if rec.quantidade_requisitada == 0:
                    rec.pode_comprar = False
                    rec.vai_comprar = False
                    self.cria_objeto_carrinho(rec)
                else:
                    rec.pode_comprar = True
                    self.cria_objeto_carrinho(rec)

        if self.variantes_produto_desejado_ids:
            if self.desejado_insuficiente:
                self.variantes_produto_desejado_ids.alt_flt_estoque.alt_flt_estoque = True
                self.cria_objeto_carrinho(self.variantes_produto_desejado_ids)
            else:
                self.variantes_produto_desejado_ids.alt_flt_estoque = False
                self.cria_objeto_carrinho(self.variantes_produto_desejado_ids)

        if self.acessorio_alternativo:
            for rec in self.acessorio_alternativo:
                if rec.quantidade_requisitada == 0:
                    rec.pode_comprar = False
                    rec.vai_comprar = False
                    self.cria_objeto_carrinho(rec)
                else:
                    rec.pode_comprar = True
                    self.cria_objeto_carrinho(rec)

        if self.produto_alternativo_id:
            if self.desejado_insuficiente:
                self.cria_objeto_carrinho(self.produto_alternativo_id)
            else:
                self.cria_objeto_carrinho(self.produto_alternativo_id)
        vals_list_retorno = {
            'alternativo_check': False,
            'variante_check': False,
            'produto_alternativo_id': False,
            'variantes_produto_desejado_ids': False,
            'desejado_check': False,
        }
        record = self.env['cotacao.wizard'].browse(cotacao_id)
        record.write(vals_list_retorno)

        return
    # def cria_concorrente(self):
    #     ctx = dict()
    #     ctx.update({
    #
    #         'default_cliente': self.cliente.id,
    #     })
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'nome',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'product_id',
    #         'views': [
    #             [
    #                 self.env.ref("cotacao.concorrente_form").id,
    #                 'form']
    #         ],
    #         'context': ctx,
    #         'target': 'new'
    #     }


