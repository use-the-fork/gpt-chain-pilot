import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import AddIcon from '@mui/icons-material/Add';
import { Box } from '@mui/material';

import { AccentButton, useChatInteract } from '@gpt-chain/components';

import NewChatDialog from './newChatDialog';

export default function NewChatButton() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { clear } = useChatInteract();

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleConfirm = () => {
    clear();
    navigate('/');
    handleClose();
  };

  return (
    <Box>
      <AccentButton
        id="new-chat-button"
        variant="outlined"
        onClick={handleClickOpen}
        startIcon={<AddIcon />}
      >
        New Chat
      </AccentButton>
      <NewChatDialog
        open={open}
        handleClose={handleClose}
        handleConfirm={handleConfirm}
      />
    </Box>
  );
}
