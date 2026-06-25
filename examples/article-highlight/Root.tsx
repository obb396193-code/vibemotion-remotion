import { Composition } from "remotion";
import { ArticleHighlight } from "./ArticleHighlight";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ArticleHighlight"
        component={ArticleHighlight}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
