import Dashboard from "../views/Dashboard.js";
import Profile from "../views/Profile.js";
import Signin from "../views/Signin.js";

const navigateTo = url => {
    history.pushState(null, null, url);
    router();
};

 // Code below is there to set the HTML page up as one document with multiple views that changes the page.
 // Route set out to determine which view appears and a communication is sent to the console to confirm it. 

const router = async ()=> {
    const routes = [
        { path: "/dashboard", view: Dashboard },
        { path: "/profile", view: Profile},
        { path: "/", view: Signin}
    ]

    //Test each route for match
    const potentialMatches = routes.map(route => {
        return {
            route: route,
            isMatch: location.pathname === route.path
        };
    });
    let match = potentialMatches.find(potentialMatch => potentialMatch.isMatch);
    if (!match) {
        match = {
        route: routes[0],
        isMatch:true
        };
    };
    const view = new match.route.view();
    document.querySelector("#app").innerHTML = await view.getHtml();
};

window.addEventListener("popstate", router);

document.addEventListener("DOMContentLoaded", () => {
    document.body.addEventListener("click", e => {
        if (e.target.matches("[data-link]")){
            e.preventDefault();
            navigateTo(e.target.href);
        }
    });

    router();
});