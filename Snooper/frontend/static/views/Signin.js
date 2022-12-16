import AbstractView from "./AbstractView.js";

export default class extends AbstractView {
    constructor(params) {
        super(params);
        this.setTitle("The Snooper | Sign In");
    }

    async getHtml() {
        return `
        <link rel="stylesheet" href="/static/css/signin.css">
        <div class="logo">
                  <img src="./static/logos/logo-gr.png" class="img-fluid">
        </div>
        <div class="container1">
        <form class="form" id="login">
            <h1 class="form__title">Login</h1>
            <div class="form__message form__message__error"></div>
            <div class="form__input-group">
                <input type="text" class="form__input" autofocus placeholder="Email">
                <div class="form__input-error-message"></div>
            </div>
            <div class="form__input-group">
                <input type="password" class="form__input" autofocus placeholder="Password">
                <div class="form__input-error-message"></div>
            </div>
            <button class="form__button" type="submit">Submit</button>
        </form>
    </div>
        `;
    }
}