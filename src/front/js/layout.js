import React, { useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import ScrollToTop from "./component/scrollToTop";
import { BackendURL } from "./component/backendURL";

import { Home } from "./pages/home";
import { Demo } from "./pages/demo";
import { Single } from "./pages/single";
import injectContext from "./store/appContext";

import { Navbar } from "./component/navbar";
import { Footer } from "./component/footer";
import { CustomerSignup } from "./pages/CustomerSignup";
import { CustomerLogin } from "./pages/CustomerLogin";
import { UserLogin } from "./pages/UserLogin";

//create your first component
const Layout = () => {

    const [isLoggedIn, setIsLoggedIn] = useState(false);
    //the basename is used when your project is published in a subdirectory and not in the root of the domain
    // you can set the basename on the .env file located at the root of this project, E.g: BASENAME=/react-hello-webapp/
    const basename = process.env.BASENAME || "";

    if(!process.env.BACKEND_URL || process.env.BACKEND_URL == "") return <BackendURL/ >;

    return (
        <div>
            <BrowserRouter basename={basename}>
                <ScrollToTop>
                    <Navbar />
                    <Routes>
                    <Route element={<Home />} path="/" />
                        <Route element={<CustomerSignup />} path="/customer-signup" />
                        <Route element={<CustomerLogin setIsLoggedIn={setIsLoggedIn} />} path="/customer-log-in" />
                        <Route element={<UserLogin setIsLoggedIn={setIsLoggedIn} />} path="/user-log-in" />
                        <Route element={<Demo />} path="/demo" />
                        <Route element={<Single />} path="/single/:theid" />
                        <Route element={<h1>Not found!</h1>} />
                    </Routes>
                    <Footer />
                </ScrollToTop>
            </BrowserRouter>
        </div>
    );
};

export default injectContext(Layout);
