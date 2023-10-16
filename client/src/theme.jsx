import {createTheme} from "@mui/material";

export const gptTheme = createTheme({
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
