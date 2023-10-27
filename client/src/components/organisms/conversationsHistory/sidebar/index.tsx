import KeyboardDoubleArrowLeftIcon from '@mui/icons-material/KeyboardDoubleArrowLeft';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import useMediaQuery from '@mui/material/useMediaQuery';
import {useState} from "react";


const DRAWER_WIDTH = 260;
const BATCH_SIZE = 20;

let _scrollTop = 0;

const _ConversationsHistorySidebar = () => {
    const isMobile = useMediaQuery('(max-width:66rem)');
    const [isChatHistoryOpen, setChatHistoryOpen] = useState(false);

    return (
        <>
            <Drawer
                className="chat-history-drawer"
                anchor="left"
                open={false}
                variant={isMobile ? 'temporary' : 'persistent'}
                hideBackdrop={!isMobile}
                onClose={() => setChatHistoryOpen(false)}

                sx={{
                    width: isChatHistoryOpen ? 'auto' : 0,
                    '& .MuiDrawer-paper': {
                        width: isChatHistoryOpen ? DRAWER_WIDTH : 0,
                        position: 'inherit',
                        gap: 1,
                        display: 'flex',
                        padding: '0px 4px',
                        backgroundImage: 'none'
                    }
                }}
            >
                <Stack
                    sx={{
                        px: 2,
                        flexDirection: 'row',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        mt: 1.5
                    }}
                >
                    <Typography
                        sx={{
                            fontSize: 16,
                            fontWeight: 600,
                            color: (theme) => theme.palette.text.primary
                        }}
                    >
                        Chat History
                    </Typography>
                    <IconButton edge="end" onClick={() => setChatHistoryOpen(false)}>
                        <KeyboardDoubleArrowLeftIcon sx={{color: 'text.primary'}}/>
                    </IconButton>
                </Stack>
                <Filters/>

            </Drawer>
        </>
    );
};

const ConversationsHistorySidebar = () => {

    return <_ConversationsHistorySidebar/>;
};

export {ConversationsHistorySidebar};
