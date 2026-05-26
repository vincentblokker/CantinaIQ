import { useEffect, useRef } from "react";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

export default function Modal({ open, onClose, title, children }: ModalProps) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  // Close on backdrop click (clicks land on <dialog> itself, not its inner card)
  function onBackdropClick(e: React.MouseEvent<HTMLDialogElement>) {
    if (e.target === ref.current) onClose();
  }

  return (
    <dialog
      ref={ref}
      onClose={onClose}
      onClick={onBackdropClick}
      className="rounded-2xl shadow-2xl p-0 backdrop:bg-ink/40 backdrop:backdrop-blur-sm w-[min(900px,92vw)] max-h-[90vh] overflow-hidden border border-stone-200"
    >
      <div className="flex items-center justify-between px-6 py-4 border-b border-stone-200 bg-cream sticky top-0">
        <h2 className="font-serif text-xl text-ink">{title}</h2>
        <button
          onClick={onClose}
          aria-label="Close"
          className="text-ink-2 hover:text-tuscan transition-colors text-2xl leading-none -mr-1 px-2"
        >
          ×
        </button>
      </div>
      <div className="px-6 py-5 overflow-y-auto max-h-[calc(90vh-72px)] bg-white">
        {children}
      </div>
    </dialog>
  );
}
