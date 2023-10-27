import { ReactMarkdown } from 'react-markdown/lib/react-markdown';
import remarkGfm from 'remark-gfm';

import { Link } from '@mui/material';

import { Code } from '@gpt-chain/components';

type Props = {
  content: string;
};

export default function Markdown({ content }: Props) {
  return (
    <ReactMarkdown
      className="markdown-body"
      remarkPlugins={[remarkGfm]}
      components={{
        a: ({ children, ...props }) => (
          <Link {...props} target="_blank">
            {children}
          </Link>
        ),
        code: ({ ...props }) => <Code {...props} />
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
