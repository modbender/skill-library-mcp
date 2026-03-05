import { useEffect, useState, useRef } from 'react';

const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+";

interface DecryptedTextProps {
  text: string;
  speed?: number;
  maxIterations?: number;
  className?: string;
  parentClassName?: string;
  animateOnHover?: boolean;
  useOriginalCharsOnly?: boolean;
}

export default function DecryptedText({
  text,
  speed = 50,
  maxIterations = 10,
  className,
  parentClassName,
  animateOnHover = false,
  useOriginalCharsOnly = false,
}: DecryptedTextProps) {
  const [displayText, setDisplayText] = useState(text);
  const [isScrambling, setIsScrambling] = useState(false);
  const iterations = useRef(0);

  const revealRef = useRef<any>(null);

  useEffect(() => {
    if (!animateOnHover) {
      startScramble();
    }

    return () => {
      if (revealRef.current) clearInterval(revealRef.current);
    };
   
  }, [text, animateOnHover]);

  const startScramble = () => {
    setIsScrambling(true);
    iterations.current = 0;

    if (revealRef.current) clearInterval(revealRef.current);

    revealRef.current = setInterval(() => {
      if (iterations.current >= maxIterations) {
        setDisplayText(text);
        setIsScrambling(false);
        if (revealRef.current) clearInterval(revealRef.current);
      } else {
        setDisplayText(
          text
            .split("")
            .map((char, index) => {
              if (char === " ") return " ";
              
              if (iterations.current > index + maxIterations / 3) {
                  return char;
              }
              
              if (useOriginalCharsOnly) {
                  return text[Math.floor(Math.random() * text.length)];
              }
              
              return letters[Math.floor(Math.random() * letters.length)];
            })
            .join("")
        );
        iterations.current += 1 / 3; // slower resolve
      }
    }, speed);
  };

  return (
    <span
      className={parentClassName}
      onMouseEnter={() => {
        if (animateOnHover && !isScrambling) startScramble();
      }}
    >
      <span className={className}>{displayText}</span>
    </span>
  );
}
