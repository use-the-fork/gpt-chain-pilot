import {createBrowserRouter, Navigate} from 'react-router-dom';
import Home from "./pages/Home";

export const router = createBrowserRouter([
    {
        path: '/',
        element: <Home/>
    },
    {
        path: '/readme',
        element: <Readme/>
    },
    {
        path: '/env',
        element: <Env/>
    },
    {
        path: '/conversation/:id?',
        element: <Conversation/>
    },
    {
        path: '/element/:id',
        element: <Element/>
    },
    {
        path: '/login',
        element: <Login/>
    },
    {
        path: '/design',
        element: <Design/>
    },
    {
        path: '/login/callback',
        element: <AuthCallback/>
    },
    {
        path: '*',
        element: <Navigate replace to="/"/>
    }
]);
