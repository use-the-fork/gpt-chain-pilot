import { IImageElement } from 'src/types/element';

import { FrameElement } from './Frame';

interface Props {
  element: IImageElement;
}

const handleImageClick = (name: string, src: string) => {
  const link = document.createElement('a');
  link.href = src;
  link.target = '_blank';
  link.download = name;
  link.style.display = 'none';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const ImageElement = ({ element }: Props) => {
  const src = element.url || URL.createObjectURL(new Blob([element.content!]));

  return (
    <FrameElement>
      <img
        className={`${element.display}-image`}
        src={src}
        onClick={() => {
          if (element.display === 'inline') {
            const name = `${element.name}.png`;
            handleImageClick(name, src);
          }
        }}
        style={{
          objectFit: 'cover',
          maxWidth: '100%',
          margin: 'auto',
          height: 'auto',
          display: 'block',
          cursor: element.display === 'inline' ? 'pointer' : 'default'
        }}
        alt={element.name}
        loading="lazy"
      />
    </FrameElement>
  );
};

export { ImageElement };
