import { useRecoilValue } from 'recoil';

import { Stack, Typography } from '@mui/material';

import { settingsState } from 'state/settings';


export default function WaterMark() {
  const { theme } = useRecoilValue(settingsState);
  return (
    <Stack mx="auto">
      <a
        href="#"
        target="_blank"
        style={{
          display: 'flex',
          alignItems: 'center',
          textDecoration: 'none'
        }}
      >
        <Typography fontSize="12px" color="text.secondary">
          ASSA ABLOY LOGO HERE
        </Typography>
      </a>
    </Stack>
  );
}