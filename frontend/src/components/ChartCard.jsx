export default function ChartCard({ title, subtitle, children, height = 300 }) {
    return (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-800">{title}</h3>
            {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
            <div className="mt-4 w-full" style={{ height }}>
                {children}
            </div>
        </div>
    );
}