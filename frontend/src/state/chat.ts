import { atom } from 'recoil';

import { IFileElement } from '@gpt-chain/components';

export const attachmentsState = atom<IFileElement[]>({
  key: 'Attachments',
  default: []
});
