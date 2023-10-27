import {createTheme} from "@mui/material";

export const gptTheme = createTheme({
    palette: {
        text: {}
    },
    components: {
        // Name of the component
        MuiButton: {
            styleOverrides: {
                // Name of the slot
                root: {
                    // Some CSS
                    fontSize: '1rem',
                },
            },
        },
    },
});
