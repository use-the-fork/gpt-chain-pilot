import App from './App';


export default function AppWrapper() {

    //const {isAuthenticated, isReady} = useAuth();

    const isReady = true;
    const isAuthenticated = true;


    if (!isReady) {
        return null;
    }

    return <App/>;
}
