import { IMessageElement } from 'src/types/element';

import { AudioElement } from './Audio';
import { FileElement } from './File';
import { ImageElement } from './Image';
import { PDFElement } from './PDF';
import { TextElement } from './Text';
import { VideoElement } from './Video';

interface ElementProps {
  element?: IMessageElement;
}

const Element = ({ element }: ElementProps): JSX.Element | null => {
  switch (element?.type) {
    case 'file':
      return <FileElement element={element} />;
    case 'image':
      return <ImageElement element={element} />;
    case 'text':
      return <TextElement element={element} />;
    case 'pdf':
      return <PDFElement element={element} />;
    case 'audio':
      return <AudioElement element={element} />;
    case 'video':
      return <VideoElement element={element} />;
    default:
      return null;
  }
};

export { Element };
