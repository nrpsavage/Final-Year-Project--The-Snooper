import AbstractView from "./AbstractView.js";

export default class extends AbstractView {
    constructor(params) {
        super(params);
        this.setTitle("The Snooper | Profile");
    }

    async getHtml() {
        return `
            <h1>Profile</h1>
            <p>Manage your privacy and configuration.</p>
            <div class="box2">User Assets</div>
            <div class="box3">User Details</div>
        `;
    }
}