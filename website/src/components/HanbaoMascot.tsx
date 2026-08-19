/**
 * Hanbao mascot (same as logo symbol). Used in Hero and Nav.
 */
import { CatPawIcon } from "./CatPawIcon";

interface HanbaoMascotProps {
  size?: number;
  className?: string;
}

export function HanbaoMascot({
  size = 80,
  className = "",
}: HanbaoMascotProps) {
  return <CatPawIcon size={size} className={className} />;
}
