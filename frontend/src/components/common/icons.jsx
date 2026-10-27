const base = { width: 20, height: 20, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": true };
const Icon = ({ children, size = 20, ...rest }) => (
  <svg {...base} width={size} height={size} {...rest}>{children}</svg>
);
export const MenuIcon = (p) => <Icon {...p}><path d="M4 6h16M4 12h16M4 18h16" /></Icon>;
export const PlusIcon = (p) => <Icon {...p}><path d="M12 5v14M5 12h14" /></Icon>;
export const PencilIcon = (p) => <Icon {...p}><path d="M12 20h9M16.5 3.5a2.1 2.1 0 013 3L7 19l-4 1 1-4z" /></Icon>;
export const TrashIcon = (p) => <Icon {...p}><path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14M10 11v5M14 11v5" /></Icon>;
export const SendIcon = (p) => <Icon {...p}><path d="M22 2L11 13M22 2l-7 20-4-9-9-4z" /></Icon>;
export const XIcon = (p) => <Icon {...p}><path d="M18 6L6 18M6 6l12 12" /></Icon>;
export const CheckIcon = (p) => <Icon {...p}><path d="M20 6L9 17l-5-5" /></Icon>;
export const LogoutIcon = (p) => <Icon {...p}><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" /></Icon>;
export const AlertIcon = (p) => <Icon {...p}><path d="M12 9v4M12 17h.01M10.3 3.9L1.8 18a2 2 0 001.7 3h17a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z" /></Icon>;
export const RetryIcon = (p) => <Icon {...p}><path d="M3 12a9 9 0 109-9 9 9 0 00-6.7 3L3 8M3 3v5h5" /></Icon>;
export const BookIcon = (p) => <Icon {...p}><path d="M4 19.5A2.5 2.5 0 016.5 17H20V3H6.5A2.5 2.5 0 004 5.5zM4 19.5V21h16" /></Icon>;
export const HangerIcon = (p) => <Icon {...p}><path d="M12 7a2 2 0 10-2-2M12 7v2l9 6a1.5 1.5 0 01-.8 2.7H3.8A1.5 1.5 0 013 15z" /></Icon>;
