import CloseIcon from '@mui/icons-material/Close';
import { Box } from '@mui/material';

import { GreyButton, useChatData, useChatInteract } from '@gpt-chain/components';

export default function StopButton() {
  const { loading } = useChatData();
  const { stopTask } = useChatInteract();

  if (!loading) {
    return null;
  }

  const handleClick = () => {
    stopTask();
  };

  return (
    <Box margin="auto">
      <GreyButton
        id="stop-button"
        startIcon={<CloseIcon />}
        variant="contained"
        onClick={handleClick}
      >
        Stop task
      </GreyButton>
    </Box>
  );
}
