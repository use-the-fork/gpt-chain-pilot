import { NotificationCount } from 'src/NotificationCount';
import { grey, primary } from 'theme/index';

import MMenuItem from '@mui/material/MenuItem';

import { SelectItem } from './SelectInput';

type MenuItemProps = {
  isDarkMode: boolean;
  item: SelectItem;
  selected: boolean;
  value: string | number;
};

const MenuItem = ({
  item,
  value,
  selected,
  isDarkMode,
  ...props
}: MenuItemProps) => (
  <MMenuItem
    {...props}
    key={value}
    sx={{
      display: 'flex',
      justifyContent: 'space-between',
      fontWeight: 500,
      fontSize: '14px',
      color: (isDarkMode && grey[400]) || (selected ? primary[500] : grey[700]),
      '&:hover': {
        backgroundColor: isDarkMode ? grey[800] : primary[50],
        color: isDarkMode ? grey[400] : primary[500],
        '& .notification-count': {
          backgroundColor: isDarkMode ? grey[850] : primary[100],
          color: isDarkMode ? grey[400] : primary[500]
        }
      }
    }}
  >
    {item.label || item.value}
    {item.notificationCount ? (
      <NotificationCount count={item.notificationCount} />
    ) : null}
  </MMenuItem>
);

export { MenuItem };
