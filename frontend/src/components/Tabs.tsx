interface TabsProps {
  tabs: string[];
  active: string;
  onChange: (tab: string) => void;
}

export function Tabs({ tabs, active, onChange }: TabsProps) {
  return (
    <div className="flex flex-wrap gap-2 border-b border-line pb-3">
      {tabs.map((tab) => (
        <button
          key={tab}
          onClick={() => onChange(tab)}
          className={`rounded-md px-3 py-2 text-sm ${active === tab ? "bg-sky-500 text-white" : "bg-panel text-slate-300 hover:bg-white/5"}`}
        >
          {tab}
        </button>
      ))}
    </div>
  );
}

