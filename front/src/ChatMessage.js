import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Box } from '@mui/material';

const ChatMessage = ({ text }) => {
  return (
    <Box
      sx={{
        bgcolor: '#f0f0f0',
        borderRadius: 2,
        p: 2,
        whiteSpace: 'pre-wrap',
        fontFamily: 'Roboto, sans-serif',
        fontSize: '1rem',
      }}
    >
      <ReactMarkdown>{text}</ReactMarkdown>
    </Box>
  );
};

export default ChatMessage;
