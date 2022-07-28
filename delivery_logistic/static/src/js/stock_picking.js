odoo.define('delivery_logistic.stock_picking.tree', function (require) {
    "use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    var QWeb = core.qweb;

    var StockPickingListController = ListController.extend({
        /**
         * Extends the renderButtons function of ListView by adding a button
         * on the stock_picking list.
         *
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments);
            this.$buttons.append($(QWeb.render("StockPickingListView.button_trip_generator", this)));
            var self = this;
            this.$buttons.on('click', '.o_button_trip_generator', function () {
                if (self.getSelectedIds().length == 0) {
                    return;
                }
                return self._rpc({
                    model: 'stock.picking',
                    method: 'action_trip_generator',
                    args: [self.getSelectedIds()],
                }).then(function (results) {
                    self.do_action(results);
                });
            });
        }
    });


    var StockPickingAddDeliveryListController = ListController.extend({
        /**
         * Extends the renderButtons function of ListView by adding a button
         * on the stock_picking list.
         *
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments);
            this.$buttons.append($(QWeb.render("StockPickingAddDeliveryListView.button_add_delivery", this)));
            var self = this;
            this.$buttons.on('click', '.o_button_add_delivery', function () {
                if (self.getSelectedIds().length == 0) {
                    return;
                }
                return self._rpc({
                    model: 'stock.picking',
                    method: 'action_add_delivery',
                    args: [self.getSelectedIds()],
                    context: self.initialState.context,
                }).then(function (results) {
                    self.do_action(results);
                });
            });
        }
    });

    var StockPickingListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: StockPickingListController
        }),
    });

    viewRegistry.add('stock_picking_delivery_logistic_tree', StockPickingListView);

    var StockPickingAddDeliveryListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: StockPickingAddDeliveryListController
        }),
    });

    viewRegistry.add('stock_picking_add_delivery_tree', StockPickingAddDeliveryListView);
});
