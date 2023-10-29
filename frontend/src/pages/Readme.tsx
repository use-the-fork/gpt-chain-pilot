import { useRecoilValue } from 'recoil';

import Page from 'pages/Page';

import Box from '@mui/material/Box';

import WelcomeScreen from 'components/organisms/chat/Messages/welcomeScreen';

import { projectSettingsState } from 'state/project';

export default function Readme() {
  const projectSettings = useRecoilValue(projectSettingsState);

  return (
    <Page>
      <Box my={2} display="flex" flexGrow={1}>
        <WelcomeScreen markdown={projectSettings?.markdown} />
      </Box>
    </Page>
  );
}
