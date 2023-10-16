import './App.css';
import Home from "./pages/Home";
import Login from "./pages/Login";
import LoginForm from "./components/login/LoginForm";
import {Navigate, Route, Routes} from "react-router-dom";
import {ThemeProvider} from "@mui/material";
import {gptTheme} from "./theme";
import { useContext } from "react";
import { AuthContext } from "./context/AuthContext";

function App() {
    const { currentUser } = useContext(AuthContext);

    const RequireAuth = ({ children }) => {
        return currentUser ? children : <Navigate to="auth/login" />;
    };

  return (
    <div className="App">
        <ThemeProvider theme={gptTheme}>
          <Routes>
            <Route
                index
                exact
                path="/"
                element={
                    <RequireAuth>
                        <Home />
                    </RequireAuth>
                }
            />
              <Route exact path="auth/login" element={<Login />} />
              <Route exact path="login" element={<LoginForm />} />
          </Routes>
        </ThemeProvider>
    </div>
  );
}

export default App;
