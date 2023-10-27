import {Alert, Box, Stack} from '@mui/material';

import {ConversationsHistorySidebar} from '@/components/organisms/conversationsHistory/sidebar';
import OpenChatHistoryButton from '@/components/organisms/conversationsHistory/sidebar/OpenChatHistoryButton';
import Header from '@/components/organisms/header';

type Props = {
    children: JSX.Element;
};

const Page = ({children}: Props) => {


    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                width: '100%'
            }}
        >
            <Header/>
            {!isAuthenticated ? (
                <Alert severity="error">You are not part of this project.</Alert>
            ) : (
                <Stack direction="row" height="100%" width="100%" overflow="auto">
                    <ConversationsHistorySidebar/>
                    <OpenChatHistoryButton mode={'desktop'}/>
                    {children}
                </Stack>
            )}
        </Box>
    );
};

export default Page;
