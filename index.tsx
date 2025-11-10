import {
  Box,
  IconButton,
  Image,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Tooltip,
} from '@chakra-ui/react';
import { useState } from 'react';
import {
  AiOutlineMail,
  AiOutlineMessage,
  AiOutlinePhone,
} from 'react-icons/ai';
import ChatWithUsIcon from '../shared/assets/img/chat-with-us-icon.svg';

interface ChatButtonProps {
  salesButtonAction: () => void;
}

export const ChatButton = ({ salesButtonAction }: ChatButtonProps) => {
  const [showOptions, setShowOptions] = useState(false);

  const openChat = () => {
    if (window?.Intercom) {
      window?.Intercom('show');
    }
  };

  const openEmail = () => {
    window.open('mailto:support@devdynamics.ai');
  };
  return (
    <Box
      alignSelf={'center'}
      borderRadius={'4px'}
      border={'1px solid #4d4dff'}
      _hover={{ backgroundColor: 'transparent' }}
      height={'95%'}
    >
      <Menu>
        <Tooltip
          aria-label="Talk to us"
          label="Talk to us"
          hasArrow
          placement="bottom"
        >
          <MenuButton>
            <IconButton
              aria-label="Talk to us"
              variant="ghost"
              bg="transparent"
              color="text.primary"
              _hover={{ bg: 'transparent' }}
              onClick={() => setShowOptions(!showOptions)}
              icon={<Image src={ChatWithUsIcon} />}
            />
          </MenuButton>
        </Tooltip>
        <MenuList mr={'20px'}>
          <MenuItem onClick={openChat} icon={<AiOutlineMessage size={20} />}>
            Chat with us
          </MenuItem>
          <MenuItem
            onClick={salesButtonAction}
            icon={<AiOutlinePhone size={20} />}
          >
            Talk to us
          </MenuItem>
          <MenuItem onClick={openEmail} icon={<AiOutlineMail size={20} />}>
            Email us
          </MenuItem>
        </MenuList>
      </Menu>
    </Box>
  );
};
