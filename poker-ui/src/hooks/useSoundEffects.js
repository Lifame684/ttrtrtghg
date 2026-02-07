import { useCallback } from 'react';

const sounds = {
};

export const useSoundEffects = () => {
  const playSound = useCallback((type) => {
    const audio = sounds[type];
    if (audio) {
      audio.currentTime = 0;
      audio.play().catch(e => console.log("Sound play failed", e));
    }
  }, []);

  return { playSound };
};
