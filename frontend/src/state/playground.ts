import { atom } from 'recoil';

import { IPlayground, PromptMode } from '@gpt-chain/components';

export const playgroundState = atom<IPlayground | undefined>({
  key: 'Playground',
  default: undefined
});

export const variableState = atom<string | undefined>({
  key: 'PlaygroundVariable',
  default: undefined
});

export const modeState = atom<PromptMode>({
  key: 'PlaygroundMode',
  default: 'Template'
});
