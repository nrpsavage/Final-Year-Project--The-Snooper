import AbstractView from "./AbstractView.js";

export default class extends AbstractView {
    constructor(params) {
        super(params);
        this.setTitle("The Snooper | Sign In");
    }

    async getHtml() {
        // Sign In has seperate style sheet to begin with due to testing and difficulties getting code to work.
        return `
        <link rel="stylesheet" href="/static/css/signin.css">
        <div class="logo">
                  <img src="./static/logos/logo-gr.png" class="img-fluid">
        </div>
        <div class="container1">
        <form id="signin" onsubmit="return log()">
            <h1 class="form__title">Login</h1>
            <input type="text" placeholder="Email" id="email" autocomplete="off" >
            <input type="password" placeholder="Password" id="pass" required>
            <button id="login" type="submit" >REGISTER</button>
        </form>
    </div>
        `;
    }
    
}