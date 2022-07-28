odoo.define('delivery_logistic.trip.tree', function (require) {
    "use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    var QWeb = core.qweb;

    var TripListController = ListController.extend({
        /**
         * Extends the renderButtons function of ListView by adding a button
         * on the trip list.
         *
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments);
            this.$buttons.append($(QWeb.render("TripListView.buttons_trip_final", this)));
            var self = this;
            this.$buttons.on('click', '.o_button_trip_final', function () {
                if (self.getSelectedIds().length == 0) {
                    return;
                }
                return self._rpc({
                    model: 'delivery_logistic.trip',
                    method: 'action_final_complete',
                    args: [self.getSelectedIds()],
                }).then(function (results) {
                    self.do_action(results);
                });
            });
            this.$buttons.on('click', '.o_button_trip_final_incomplete', function () {
                if (self.getSelectedIds().length == 0) {
                    return;
                }
                return self._rpc({
                    model: 'delivery_logistic.trip',
                    method: 'action_final_incomplete',
                    args: [self.getSelectedIds()],
                }).then(function (results) {
                    self.do_action(results);
                });
            });
        }
    });

    var TripListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: TripListController
        }),
    });

    viewRegistry.add('trip_final_tree', TripListView);
});
