odoo.define('point_of_sale.ValidarImpresion', function (require) {
    "use strict";
    const InvoiceButton = require('point_of_sale.InvoiceButton');

    const Registries = require('point_of_sale.Registries');

    const PosBotonValidar = InvoiceButton => class extends InvoiceButton {
        async _downloadInvoice(orderId) {
            try {
                const [orderWithInvoice] = await this.rpc({
                    method: 'read',
                    model: 'pos.order',
                    args: [orderId, ['account_move']],
                    kwargs: { load: false },
                });
                if (this.env.pos.config.disable_pdf_invoice_download && this.env.pos.config.disable_pdf_invoice_download === true) {
                    return;
                }
                if (orderWithInvoice && orderWithInvoice.account_move) {
                    await this.env.pos.do_action('fel.reporte_factura', {
                        additional_context: {
                            active_ids: [orderWithInvoice.account_move],
                        },
                    });
                }
            } catch (error) {
                if (error instanceof Error) {
                    throw error;
                } else {
                    // NOTE: error here is most probably undefined
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Network Error'),
                        body: this.env._t('Unable to download invoice.'),
                    });
                }
            }
        }
    }
    Registries.Component.extend(InvoiceButton, PosBotonValidar);

    return InvoiceButton;
});

odoo.define('point_of_sale.BotonImpresion', function (require) {
    "use strict";


    const models = require('point_of_sale.models');

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        push_and_invoice_order: function (order) {
            var self = this;
            return new Promise((resolve, reject) => {
                if (!order.get_client()) {
                    reject({ code: 400, message: 'Missing Customer', data: {} });
                } else {
                    var order_id = self.db.add_order(order.export_as_JSON());
                    self.flush_mutex.exec(async () => {
                        try {
                            const server_ids = await self._flush_orders([self.db.get_order(order_id)], {
                                timeout: 30000,
                                to_invoice: true,
                            });
                            if (server_ids.length) {
                                const [orderWithInvoice] = await self.rpc({
                                    method: 'read',
                                    model: 'pos.order',
                                    args: [server_ids, ['account_move']],
                                    kwargs: { load: false },
                                });
                                if (self.config.disable_pdf_invoice_download && self.config.disable_pdf_invoice_download === true) {
                                    return resolve(server_ids);
                                }
                                await self
                                    .do_action('fel.reporte_factura', {
                                        additional_context: {
                                            active_ids: [orderWithInvoice.account_move],
                                        },
                                    })
                                    .catch(() => {
                                        reject({ code: 401, message: 'Backend Invoice', data: { order: order } });
                                    });
                            } else {
                                reject({ code: 401, message: 'Backend Invoice', data: { order: order } });
                            }
                            resolve(server_ids);
                        } catch (error) {
                            reject(error);
                        }
                    });
                }
            });
        },
        // _save_to_server: async function (orders, options) {
        //     let self = this;
        //     let order_id = null;
        //     if (orders.length === 1) {
        //         order_id = orders[0].id
        //     }
        //     return new Promise((resolve, reject) => {
        //         _super_posmodel._save_to_server.apply(this, arguments).then(async (res) => {
        //             resolve(res);
        //         }).catch(error => {
        //             if (order_id && error.message?.data?.message.startsWith('[CLR-ACT-ORDR]')) {
        //                 console.log(error);
        //                 let order = self.db.get_order(order_id);
        //                 // console.log(order);
        //                 let client = self.db.get_partner_by_id(order.data.partner_id);
        //                 // console.log(client);
        //                 // let popUpMessage = `Se eliminó la orden No. ${order_id} ya que el Nit '${client.vat}' del cliente '${client.name}' es incorrecto, por favor modifique el Nit antes de generar una nueva orden al cliente.`

        //                 self.db.remove_order(order_id);
        //                 let currentOrder = self.get_order();
        //                 if (currentOrder && currentOrder.uid === order_id) {
        //                     self.delete_current_order();
        //                 } else {
        //                     self.db.remove_unpaid_order({ uid: order_id });
        //                 }

        //                 self.add_new_order();

        //                 // console.log("Despues de elimnar");
        //                 // console.log(self.db.get_orders());
        //                 // Gui.showPopup("ErrorPopup", {
        //                 //     'title': _t("Error de validación de Nit."),
        //                 //     'body': _t(popUpMessage),
        //                 // });

        //             }
        //             reject(error);
        //         })
        //     })
        // },
    });
});