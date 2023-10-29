import { ClientError } from 'api';
import { ChainlitAPI } from 'api/chainlitApi';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { useRecoilValue } from 'recoil';

import DeleteOutline from '@mui/icons-material/DeleteOutline';
import LoadingButton from '@mui/lab/LoadingButton';
import { IconButton } from '@mui/material';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

import { accessTokenState } from 'state/user';

interface Props {
  conversationId: string;
  onDelete: () => void;
}

const DeleteConversationButton = ({ conversationId, onDelete }: Props) => {
  const [open, setOpen] = useState(false);
  const accessToken = useRecoilValue(accessTokenState);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleConfirm = async () => {
    await toast.promise(
      ChainlitAPI.deleteConversation(conversationId, accessToken),
      {
        loading: 'Deleting conversation...',
        success: 'Conversation deleted!',
        error: (err) => {
          if (err instanceof ClientError) {
            return <span>{err.message}</span>;
          } else {
            return <span></span>;
          }
        }
      }
    );
    onDelete();
    handleClose();
  };

  return (
    <div>
      <IconButton size="small" onClick={handleClickOpen} sx={{ p: '2px' }}>
        <DeleteOutline sx={{ width: 16, height: 16 }} />
      </IconButton>
      {open && (
        <Dialog
          open={open}
          onClose={handleClose}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
          PaperProps={{
            sx: {
              backgroundImage: 'none'
            }
          }}
        >
          <DialogTitle id="alert-dialog-title">
            {'Delete conversation?'}
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description">
              This will delete the conversation as well as it's messages and
              elements.
            </DialogContentText>
          </DialogContent>
          <DialogActions sx={{ color: 'text.secondary', p: 2 }}>
            <Button variant="outlined" color="inherit" onClick={handleClose}>
              Cancel
            </Button>
            <LoadingButton
              variant="outlined"
              color="primary"
              onClick={handleConfirm}
              autoFocus
            >
              Confirm
            </LoadingButton>
          </DialogActions>
        </Dialog>
      )}
    </div>
  );
};

export { DeleteConversationButton };
