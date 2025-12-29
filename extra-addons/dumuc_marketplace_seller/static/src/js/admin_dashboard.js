/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";

class AdminDashboard extends Component {
    static template = "dumuc_admin_dashboard";

    setup() {
        this.state = useState({ data: { counts: {}, pending_items: [] } });

        onWillStart(async () => {
            this.state.data = await this.env.services.rpc(
                "/dumuc/admin/dashboard/data",
                {}
            );
            console.log(this.state.data);
        });
    }

    async approveListing(ev) {
        const id = ev.target.dataset.id;
        await this.env.services.rpc("/dumuc/admin/listing/approve", { listing_id: id });
        this.state.data = await this.env.services.rpc("/dumuc/admin/dashboard/data", {});
    }

    rejectListing(ev) {
        const id = ev.target.dataset.id;
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            res_model: "dumuc.listing.reject.wizard",
            view_mode: "form",
            target: "new",
            context: { default_listing_id: id },
        });
    }
}

registry.category("actions").add("dumuc_admin_dashboard", AdminDashboard);
