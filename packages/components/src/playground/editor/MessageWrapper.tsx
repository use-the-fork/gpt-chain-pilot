import { PlaygroundContext } from 'contexts/PlaygroundContext';
import React, { useContext, useState } from 'react';
import { SelectInput } from 'src/inputs';
import { IPromptMessage, PromptMessageRole } from 'src/types';

import Box from '@mui/material/Box';
import { SelectChangeEvent } from '@mui/material/Select';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

const roles = ['Assistant', 'System', 'User'];

interface MessageWrapperProps {
  canSelectRole?: boolean;
  children: React.ReactElement;
  index?: number;
  message?: IPromptMessage;
  role?: string;
  name?: string;
}

const MessageWrapper = ({
  canSelectRole,
  children,
  index,
  message,
  role,
  name
}: MessageWrapperProps): JSX.Element => {
  const [showSelectRole, setShowSelectRole] = useState(false);
  const { setPlayground } = useContext(PlaygroundContext);

  const onRoleSelected = (event: SelectChangeEvent) => {
    const role = event.target.value as PromptMessageRole;

    if (role) {
      setPlayground((old) => ({
        ...old,
        prompt: {
          ...old!.prompt!,
          messages: old?.prompt?.messages?.map((message, mIndex) => ({
            ...message,
            ...(mIndex === index ? { role } : {}) // Update role if it's the selected message
          }))
        }
      }));
    }

    setShowSelectRole(false);
  };

  return (
    <Box key={index}>
      <Box
        sx={{
          border: (theme) => `1px solid ${theme.palette.divider}`,
          borderRadius: 1
        }}
      />
      <Stack
        direction="row"
        width="100%"
        sx={{
          gap: 2,
          flex: 10,
          paddingY: 1,
          '&:hover': {
            background: (theme) => theme.palette.background.paper
          }
        }}
      >
        <Box sx={{ flex: 1, paddingLeft: 2 }}>
          {!showSelectRole ? (
            <Typography
              onClick={() => canSelectRole && setShowSelectRole(true)}
              color="text.primary"
              sx={{
                p: 1,
                borderRadius: 0.5,
                marginTop: 1,
                cursor: canSelectRole ? 'pointer' : 'default',
                fontSize: '12px',
                fontWeight: 700,
                width: 'fit-content',
                ...(canSelectRole && {
                  '&:hover': {
                    backgroundColor: (theme) => theme.palette.divider
                  }
                })
              }}
            >
              {role}
            </Typography>
          ) : (
            <SelectInput
              onClose={() => setShowSelectRole(false)}
              defaultOpen
              items={roles.map((role) => ({
                label: role,
                value: role.toLowerCase()
              }))}
              id="role-select"
              value={message?.role}
              onChange={onRoleSelected}
              sx={{ width: 'fit-content' }}
              iconSx={{
                px: 0,
                marginRight: '2px !important'
              }}
            />
          )}
          {name ? (
            <Typography
              color="text.secondary"
              variant="caption"
              sx={{
                ml: 1,
                width: 'fit-content'
              }}
            >
              {name}
            </Typography>
          ) : null}
        </Box>
        <Box width="100%" flex={8}>
          {children}
        </Box>
      </Stack>
    </Box>
  );
};

export default MessageWrapper;
