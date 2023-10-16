import React from "react";
import {Box, CircularProgress} from "@mui/material";

const Loading = () => {
	const override = {
		color: "#fff",
		loading: true,
	};

	return (
		<div>
			<Box sx={{ display: 'flex' }}>
				<CircularProgress />
			</Box>
		</div>
	);
};

export default Loading;
